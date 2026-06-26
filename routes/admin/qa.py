from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import Question
from models.db import db
from utils.admin import admin_required, approve_question_record


admin_qa_bp = Blueprint("admin_qa", __name__, url_prefix="/admin")


@admin_qa_bp.route("/questions/<int:question_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == "POST":
        question.title = request.form.get("title", "").strip() or question.title
        question.body = request.form.get("body", "").strip() or question.body
        question.tags = request.form.get("tags", "").strip()
        question.version = request.form.get("version", "").strip()
        if request.form.get("action") == "approve":
            approve_question_record(question)
            flash("Question approved and published.", "success")
            return redirect(request.form.get("next") or url_for("qa.questions", tab="published", question_id=question.id))
        db.session.commit()
        flash("Question saved for review.", "success")
        return redirect(request.form.get("next") or url_for("qa.questions", tab="pending", question_id=question.id))
    return render_template("admin/edit_question.html", question=question)