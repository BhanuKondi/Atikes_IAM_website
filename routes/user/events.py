from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models.db import db
from models import UpcomingEvent


events_bp = Blueprint("events", __name__, url_prefix="/events")


@events_bp.route("/")
def list_events():
    events = (
        UpcomingEvent.query.filter(
            UpcomingEvent.is_published.is_(True),
            UpcomingEvent.starts_at >= datetime.now(timezone.utc),
        )
        .order_by(UpcomingEvent.starts_at.asc())
        .all()
    )
    return render_template("user/events/events.html", events=events)


@events_bp.route("/admin/new", methods=["GET", "POST"])
@login_required
def new_event():
    if not current_user.is_admin:
        return redirect(url_for("events.list_events"))
    if request.method == "POST":
        event = UpcomingEvent()
        _apply_event_form(event)
        db.session.add(event)
        db.session.commit()
        flash("Event added.", "success")
        return redirect(url_for("events.list_events"))
    return render_template("user/events/event_form.html", event=None)


@events_bp.route("/admin/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    if not current_user.is_admin:
        return redirect(url_for("events.list_events"))
    event = UpcomingEvent.query.get_or_404(event_id)
    if request.method == "POST":
        _apply_event_form(event)
        db.session.commit()
        flash("Event updated.", "success")
        return redirect(url_for("events.list_events"))
    return render_template("user/events/event_form.html", event=event)


@events_bp.post("/admin/<int:event_id>/delete")
@login_required
def delete_event(event_id):
    if not current_user.is_admin:
        return redirect(url_for("events.list_events"))
    event = UpcomingEvent.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash("Event removed.", "success")
    return redirect(url_for("events.list_events"))


def _apply_event_form(event):
    event.title = request.form.get("title", "").strip()
    event.description = request.form.get("description", "").strip()
    event.event_type = request.form.get("event_type", "Webinar").strip() or "Webinar"
    event.organizer = request.form.get("organizer", "").strip()
    event.location = request.form.get("location", "Online").strip() or "Online"
    event.registration_url = request.form.get("registration_url", "").strip()
    event.source_url = request.form.get("source_url", "").strip()
    event.is_published = request.form.get("is_published") == "on"
    starts_at = request.form.get("starts_at", "").strip()
    ends_at = request.form.get("ends_at", "").strip()
    event.starts_at = datetime.fromisoformat(starts_at) if starts_at else datetime.now(timezone.utc)
    event.ends_at = datetime.fromisoformat(ends_at) if ends_at else None
