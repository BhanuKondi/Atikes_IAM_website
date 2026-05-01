from flask import Blueprint, render_template, request

from ..services.trends import fetch_live_trends


trends_bp = Blueprint("trends", __name__, url_prefix="/trends")


@trends_bp.route("/")
def list_trends():
    force = request.args.get("refresh") == "1"
    trends, errors, refreshed = fetch_live_trends(force=force)
    category = request.args.get("category", "All")
    categories = ["All"] + sorted({item["category"] for item in trends})
    if category != "All":
        trends = [item for item in trends if item["category"] == category]
    return render_template(
        "trends.html",
        trends=trends,
        errors=errors,
        refreshed=refreshed,
        categories=categories,
        active_category=category,
    )
