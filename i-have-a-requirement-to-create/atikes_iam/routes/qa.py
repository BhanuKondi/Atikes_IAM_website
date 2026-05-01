from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Answer, Question


qa_bp = Blueprint("qa", __name__, url_prefix="/qa")


@qa_bp.route("/")
def questions():
    tag = request.args.get("tag", "").strip().lower()
    query = Question.query
    if tag:
        query = query.filter(Question.tags.ilike(f"%{tag}%"))
    items = query.order_by(Question.created_at.desc()).all()
    return render_template("qa/list.html", questions=items, active_tag=tag)


@qa_bp.route("/ask", methods=["GET", "POST"])
@login_required
def ask_question():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        tags = request.form.get("tags", "").strip()
        if len(title) < 10 or len(body) < 20:
            flash("Please add a clear title and enough detail for experts to answer.", "error")
        else:
            question = Question(title=title, body=body, tags=tags, author=current_user)
            db.session.add(question)
            db.session.commit()
            flash("Question posted.", "success")
            return redirect(url_for("qa.question_detail", question_id=question.id))
    return render_template("qa/ask.html")


@qa_bp.route("/<int:question_id>", methods=["GET", "POST"])
def question_detail(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Sign in to answer this question.", "info")
            return redirect(url_for("auth.login", next=request.path))
        body = request.form.get("body", "").strip()
        if len(body) < 20:
            flash("Please write a useful answer with at least 20 characters.", "error")
        else:
            answer = Answer(body=body, author=current_user, question=question)
            db.session.add(answer)
            db.session.commit()
            flash("Answer posted.", "success")
            return redirect(url_for("qa.question_detail", question_id=question.id))
    answers = question.answers.order_by(Answer.created_at.desc()).all()
    return render_template("qa/detail.html", question=question, answers=answers)
