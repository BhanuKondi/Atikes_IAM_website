from flask import Blueprint, render_template, request
from flask_login import current_user

from models import Trend
from utils.trends import fetch_live_trends, get_stored_trends


trends_bp = Blueprint("trends", __name__, url_prefix="/trends")


@trends_bp.route("/")
def list_trends():
    force = request.args.get("refresh") == "1"
    search = request.args.get("q", "").strip()
    _, errors, refreshed = fetch_live_trends(force=force)

    active_tab = request.args.get("tab", "published")
    if not current_user.is_authenticated or not current_user.is_admin or active_tab not in {"published", "pending"}:
        active_tab = "published"

    selected_trend_id = request.args.get("trend_id", type=int)
    published_trends = get_stored_trends(search=search, approved_only=True)
    pending_trends = []
    if current_user.is_authenticated and current_user.is_admin:
        pending_query = Trend.query.filter_by(status="pending")
        if search:
            pattern = f"%{search}%"
            pending_query = pending_query.filter(
                Trend.title.ilike(pattern) | Trend.summary.ilike(pattern) | Trend.category.ilike(pattern)
            )
        pending_trends = pending_query.order_by(Trend.fetched_at.desc(), Trend.published_at.desc()).limit(36).all()

    trends = pending_trends if active_tab == "pending" else published_trends
    selected_trend = None
    if selected_trend_id:
        selected_trend = next((trend for trend in trends if trend.id == selected_trend_id), None)
    if selected_trend is None and trends:
        selected_trend = trends[0]

    return render_template(
        "user/trends/trends.html",
        trends=trends,
        selected_trend=selected_trend,
        published_trends=published_trends,
        pending_trends=pending_trends,
        active_tab=active_tab,
        errors=errors,
        refreshed=refreshed,
        search=search,
    )


@trends_bp.route("/<int:trend_id>")
def trend_detail(trend_id):
    trend = Trend.query.filter_by(id=trend_id, status="approved").first_or_404()
    return render_template("user/trends/trend_detail.html", trend=trend)
