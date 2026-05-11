from functools import wraps
from pathlib import Path

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Question, Trend, utcnow
from ..services.content_generation import generate_trend_content
from ..services.experts import refresh_expert_profile
from werkzeug.utils import secure_filename


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
    search = request.args.get("q", "").strip()
    pending_trends = Trend.query.filter_by(status="pending").order_by(Trend.fetched_at.desc()).limit(30).all()
    question_query = Question.query.filter_by(status="pending")
    if search:
        question_query = question_query.filter(Question.title.ilike(f"%{search}%"))
    pending_questions = question_query.order_by(Question.created_at.desc()).all()
    return render_template(
        "admin/dashboard.html",
        pending_trends=pending_trends,
        pending_questions=pending_questions,
        search=search,
    )


@admin_bp.route("/trends/<int:trend_id>")
@admin_required
def view_trend(trend_id):
    trend = Trend.query.get_or_404(trend_id)
    return render_template("admin/view_trend.html", trend=trend)


@admin_bp.post("/trends/<int:trend_id>/generate")
@admin_required
def generate_trend(trend_id):
    trend = Trend.query.get_or_404(trend_id)
    try:
        trend.generated_content = generate_trend_content(trend)
        db.session.commit()
        flash("Website content generated for review.", "success")
    except Exception as exc:
        flash(f"Could not generate content from the source site: {exc}", "error")
    return redirect(url_for("admin.view_trend", trend_id=trend.id))


@admin_bp.route("/trends/<int:trend_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_trend(trend_id):
    trend = Trend.query.get_or_404(trend_id)
    if request.method == "POST":
        trend.title = request.form.get("title", "").strip() or trend.title
        trend.summary = request.form.get("summary", "").strip()
        trend.generated_content = request.form.get("generated_content", "").strip()
        trend.image_url = request.form.get("image_url", "").strip()
        trend.category = request.form.get("category", "").strip() or trend.category
        trend.url = request.form.get("url", "").strip() or trend.url
        _save_trend_image(trend)
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
        question.version = request.form.get("version", "").strip()
        if request.form.get("action") == "approve":
            approve_question_record(question)
            flash("Question approved and published.", "success")
            return redirect(url_for("admin.dashboard"))
        db.session.commit()
        flash("Question saved for review.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/edit_question.html", question=question)


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


def approve_trend_record(trend):
    if trend.generated_content:
        trend.summary = trend.generated_content
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


def _save_trend_image(trend):
    upload = request.files.get("image")
    if not upload or not upload.filename:
        return
    filename = secure_filename(upload.filename)
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in {"jpg", "jpeg", "png", "webp", "gif"}:
        flash("Trend image skipped. Please upload JPG, PNG, WEBP, or GIF.", "error")
        return
    upload_dir = Path(current_app.root_path) / "static" / "uploads" / "trends"
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"trend-{trend.id}-{filename}"
    upload.save(upload_dir / stored_name)
    trend.image_path = f"uploads/trends/{stored_name}"
