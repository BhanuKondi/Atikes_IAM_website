from datetime import datetime, timezone

from flask import Blueprint, render_template
from flask_login import login_required

from ..models import UpcomingEvent


events_bp = Blueprint("events", __name__, url_prefix="/events")


@events_bp.route("/")
@login_required
def list_events():
    events = (
        UpcomingEvent.query.filter(
            UpcomingEvent.is_published.is_(True),
            UpcomingEvent.starts_at >= datetime.now(timezone.utc),
        )
        .order_by(UpcomingEvent.starts_at.asc())
        .all()
    )
    return render_template("events.html", events=events)
