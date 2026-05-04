from flask import Blueprint, render_template, request
from flask_login import login_required

from ..models import Trend
from ..services.trends import fetch_live_trends, get_stored_trends


trends_bp = Blueprint("trends", __name__, url_prefix="/trends")


@trends_bp.route("/")
@login_required
def list_trends():
    force = request.args.get("refresh") == "1"
    search = request.args.get("q", "").strip()
    _, errors, refreshed = fetch_live_trends(force=force)
    category = request.args.get("category", "All")
    categories = ["All"] + [
        row[0]
        for row in Trend.query.filter_by(status="approved")
        .with_entities(Trend.category)
        .distinct()
        .order_by(Trend.category)
        .all()
    ]
    trends = get_stored_trends(category=category, search=search)
    return render_template(
        "trends.html",
        trends=trends,
        errors=errors,
        refreshed=refreshed,
        categories=categories,
        active_category=category,
        search=search,
    )
