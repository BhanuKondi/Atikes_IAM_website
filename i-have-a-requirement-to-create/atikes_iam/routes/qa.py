from pathlib import Path

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Answer, Question
from ..services.experts import refresh_expert_profile


qa_bp = Blueprint("qa", __name__, url_prefix="/qa")
ALLOWED_ATTACHMENTS = {"pdf", "jpg", "jpeg", "png"}


@qa_bp.route("/")
@login_required
def questions():
    tag = request.args.get("tag", "").strip().lower()
    query = Question.query.filter_by(status="approved")
    if tag:
        query = query.filter(Question.tags.ilike(f"%{tag}%"))
    items = query.order_by(Question.created_at.desc()).all()
    return render_template("qa/list.html", questions=items, active_tag=tag)


@qa_bp.route("/ask", methods=["GET", "POST"])
@login_required
def ask_question():
    tag_options = ["SailPoint IIQ", "SailPoint IDN", "Okta", "Saviynt", "Ping Identity"]
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        version = request.form.get("version", "").strip()
        tag_choice = request.form.get("tag_choice", "").strip()
        other_tag = request.form.get("other_tag", "").strip()
        tags = other_tag if tag_choice == "Other" else tag_choice
        if len(title) < 10 or len(body) < 20:
            flash("Please add a clear title and enough detail for experts to answer.", "error")
        elif not tags:
            flash("Please choose a tag or enter another IAM tag.", "error")
        else:
            question = Question(title=title, body=body, tags=tags, version=version, author=current_user)
            db.session.add(question)
            db.session.flush()
            _save_attachment(question)
            refresh_expert_profile(current_user)
            db.session.commit()
            flash("Question submitted for admin review.", "success")
            return redirect(url_for("qa.question_detail", question_id=question.id))
    return render_template("qa/ask.html", tag_options=tag_options)


def _save_attachment(question):
    upload = request.files.get("attachment")
    if not upload or not upload.filename:
        return
    filename = secure_filename(upload.filename)
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_ATTACHMENTS:
        flash("Attachment skipped. Please upload only PDF, JPG, JPEG, or PNG files.", "error")
        return
    upload_dir = Path(current_app.root_path) / "static" / "uploads" / "questions"
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"question-{question.id}-{filename}"
    upload.save(upload_dir / stored_name)
    question.attachment_filename = filename
    question.attachment_path = f"uploads/questions/{stored_name}"


@qa_bp.route("/<int:question_id>", methods=["GET", "POST"])
@login_required
def question_detail(question_id):
    question = Question.query.get_or_404(question_id)
    can_view_pending = current_user.is_authenticated and (
        current_user.is_admin or question.author_id == current_user.id
    )
    if question.status != "approved" and not can_view_pending:
        abort(404)
    if request.method == "POST":
        body = request.form.get("body", "").strip()
        if len(body) < 20:
            flash("Please write a useful answer with at least 20 characters.", "error")
        else:
            answer = Answer(body=body, author=current_user, question=question)
            db.session.add(answer)
            db.session.flush()
            refresh_expert_profile(current_user)
            db.session.commit()
            flash("Answer submitted for admin review.", "success")
            return redirect(url_for("qa.question_detail", question_id=question.id))
    answers_query = question.answers
    if not (current_user.is_authenticated and current_user.is_admin):
        answers_query = answers_query.filter_by(status="approved")
    answers = answers_query.order_by(Answer.created_at.desc()).all()
    return render_template("qa/detail.html", question=question, answers=answers)
