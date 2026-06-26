from flask import Blueprint, flash, redirect, request, url_for

from models import Question, Trend
from models.db import db
from utils.admin import admin_required, approve_question_record, approve_trend_record


admin_approvals_bp = Blueprint("admin_approvals", __name__, url_prefix="/admin")


@admin_approvals_bp.post("/trends/<int:trend_id>/approve")
@admin_required
def approve_trend(trend_id):
    trend = Trend.query.get_or_404(trend_id)
    approve_trend_record(trend)
    flash("Trend approved and published.", "success")
    return redirect(request.referrer or url_for("trends.list_trends", tab="published", trend_id=trend.id))


@admin_approvals_bp.post("/questions/<int:question_id>/approve")
@admin_required
def approve_question(question_id):
    question = Question.query.get_or_404(question_id)
    approve_question_record(question)
    flash("Question approved and published.", "success")
    return redirect(request.referrer or url_for("qa.questions", tab="published", question_id=question.id))


@admin_approvals_bp.post("/questions/<int:question_id>/reject")
@admin_required
def reject_question(question_id):
    question = Question.query.get_or_404(question_id)
    question.status = "rejected"
    question.approved_at = None
    question.approved_by = None
    db.session.commit()
    flash("Question rejected.", "success")
    return redirect(request.referrer or url_for("qa.questions", tab="pending"))
