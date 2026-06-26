from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from models import Trend
from models.db import db
from utils.admin import admin_required, approve_trend_record
from utils.content_generation import generate_trend_content


admin_trends_bp = Blueprint("admin_trends", __name__, url_prefix="/admin")


@admin_trends_bp.route("/trends/<int:trend_id>")
@admin_required
def view_trend(trend_id):
    trend = Trend.query.get_or_404(trend_id)
    return render_template("admin/view_trend.html", trend=trend)


@admin_trends_bp.post("/trends/<int:trend_id>/generate")
@admin_required
def generate_trend(trend_id):
    trend = Trend.query.get_or_404(trend_id)
    try:
        trend.generated_content = generate_trend_content(trend)
        db.session.commit()
        flash("Website content generated for review.", "success")
    except Exception as exc:
        flash(f"Could not generate content from the source site: {exc}", "error")
    return redirect(request.form.get("next") or request.referrer or url_for("trends.list_trends", tab="pending", trend_id=trend.id))


@admin_trends_bp.post("/trends/<int:trend_id>/content")
@admin_required
def update_trend_content(trend_id):
    trend = Trend.query.get_or_404(trend_id)
    if trend.status != "pending":
        flash("Only pending trends can be edited from this review panel.", "error")
        return redirect(request.form.get("next") or request.referrer or url_for("trends.list_trends", tab="published", trend_id=trend.id))

    generated_content = request.form.get("generated_content", "").strip()
    if not generated_content:
        flash("Generated content cannot be empty.", "error")
    else:
        trend.generated_content = generated_content
        db.session.commit()
        flash("Generated content updated.", "success")
    return redirect(request.form.get("next") or request.referrer or url_for("trends.list_trends", tab="pending", trend_id=trend.id))


@admin_trends_bp.route("/trends/<int:trend_id>/edit", methods=["GET", "POST"])
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
            return redirect(request.form.get("next") or url_for("trends.list_trends", tab="published", trend_id=trend.id))
        db.session.commit()
        flash("Trend saved for review.", "success")
        return redirect(request.form.get("next") or url_for("trends.list_trends", tab="pending", trend_id=trend.id))
    return render_template("admin/edit_trend.html", trend=trend)


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