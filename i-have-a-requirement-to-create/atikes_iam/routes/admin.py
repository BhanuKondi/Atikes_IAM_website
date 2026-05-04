from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Answer, Question, Trend, utcnow
from ..services.experts import refresh_expert_profile


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route("/")
@admin_required
def dashboard():
    pending_trends = Trend.query.filter_by(status="pending").order_by(Trend.fetched_at.desc()).limit(30).all()
    pending_questions = Question.query.filter_by(status="pending").order_by(Question.created_at.desc()).all()
    pending_answers = Answer.query.filter_by(status="pending").order_by(Answer.created_at.desc()).all()
    return render_template(
        "admin/dashboard.html",
        pending_trends=pending_trends,
        pending_questions=pending_questions,
        pending_answers=pending_answers,
    )


@admin_bp.route("/trends/<int:trend_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_trend(trend_id):
    trend = Trend.query.get_or_404(trend_id)
    if request.method == "POST":
        trend.title = request.form.get("title", "").strip() or trend.title
        trend.summary = request.form.get("summary", "").strip()
        trend.category = request.form.get("category", "").strip() or trend.category
        trend.url = request.form.get("url", "").strip() or trend.url
        if request.form.get("action") == "approve":
            approve_trend_record(trend)
            flash("Trend approved and published.", "success")
            return redirect(url_for("admin.dashboard"))
        db.session.commit()
        flash("Trend saved for review.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/edit_trend.html", trend=trend)


@admin_bp.route("/questions/<int:question_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == "POST":
        question.title = request.form.get("title", "").strip() or question.title
        question.body = request.form.get("body", "").strip() or question.body
        question.tags = request.form.get("tags", "").strip()
        if request.form.get("action") == "approve":
            approve_question_record(question)
            flash("Question approved and published.", "success")
            return redirect(url_for("admin.dashboard"))
        db.session.commit()
        flash("Question saved for review.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/edit_question.html", question=question)


@admin_bp.route("/answers/<int:answer_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    if request.method == "POST":
        answer.body = request.form.get("body", "").strip() or answer.body
        if request.form.get("action") == "approve":
            approve_answer_record(answer)
            flash("Answer approved and published.", "success")
            return redirect(url_for("admin.dashboard"))
        db.session.commit()
        flash("Answer saved for review.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/edit_answer.html", answer=answer)


@admin_bp.post("/trends/<int:trend_id>/approve")
@admin_required
def approve_trend(trend_id):
    approve_trend_record(Trend.query.get_or_404(trend_id))
    flash("Trend approved and published.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/questions/<int:question_id>/approve")
@admin_required
def approve_question(question_id):
    approve_question_record(Question.query.get_or_404(question_id))
    flash("Question approved and published.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/answers/<int:answer_id>/approve")
@admin_required
def approve_answer(answer_id):
    approve_answer_record(Answer.query.get_or_404(answer_id))
    flash("Answer approved and published.", "success")
    return redirect(url_for("admin.dashboard"))


def approve_trend_record(trend):
    trend.status = "approved"
    trend.approved_at = utcnow()
    trend.approved_by = current_user
    db.session.commit()


def approve_question_record(question):
    question.status = "approved"
    question.approved_at = utcnow()
    question.approved_by = current_user
    refresh_expert_profile(question.author)
    db.session.commit()


def approve_answer_record(answer):
    answer.status = "approved"
    answer.approved_at = utcnow()
    answer.approved_by = current_user
    refresh_expert_profile(answer.author)
    db.session.commit()
