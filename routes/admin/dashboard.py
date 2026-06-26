from flask import Blueprint, render_template, request

from models import Answer, ExpertProfile, Question, Trend, UpcomingEvent, User
from utils.admin import admin_required


admin_dashboard_bp = Blueprint("admin_dashboard", __name__, url_prefix="/admin")


@admin_dashboard_bp.route("/")
@admin_required
def dashboard():
    search = request.args.get("q", "").strip()
    active_view = request.args.get("view", "dashboard")
    if active_view not in {"dashboard", "users"}:
        active_view = "dashboard"
    active_tab = request.args.get("tab", "pending")
    if active_tab not in {"pending", "published"}:
        active_tab = "pending"
    selected_trend_id = request.args.get("trend_id", type=int)
    pending_trends = Trend.query.filter_by(status="pending").order_by(Trend.fetched_at.desc()).limit(30).all()
    published_trends = Trend.query.filter_by(status="approved").order_by(Trend.approved_at.desc(), Trend.published_at.desc()).limit(30).all()
    active_trends = published_trends if active_tab == "published" else pending_trends
    selected_trend = None
    if selected_trend_id:
        selected_trend = next((trend for trend in active_trends if trend.id == selected_trend_id), None)
    if selected_trend is None and active_trends:
        selected_trend = active_trends[0]
    question_query = Question.query.filter_by(status="pending")
    if search:
        question_query = question_query.filter(Question.title.ilike(f"%{search}%"))
    pending_questions = question_query.order_by(Question.created_at.desc()).all()
    users = User.query.order_by(User.created_at.desc()).all()
    user_rows = [
        {
            "user": user,
            "approved_questions": Question.query.filter_by(author_id=user.id, status="approved").count(),
            "approved_answers": Answer.query.filter_by(author_id=user.id, status="approved").count(),
            "pending_questions": Question.query.filter_by(author_id=user.id, status="pending").count(),
            "pending_answers": Answer.query.filter_by(author_id=user.id, status="pending").count(),
        }
        for user in users
    ]
    for row in user_rows:
        row["points"] = row["user"].points or 0

    stats = {
        "users": len(users),
        "admins": sum(1 for user in users if user.is_admin),
        "published_trends": Trend.query.filter_by(status="approved").count(),
        "published_questions": Question.query.filter_by(status="approved").count(),
        "published_answers": Answer.query.filter_by(status="approved").count(),
        "experts": ExpertProfile.query.filter_by(is_listed=True).count(),
        "events": UpcomingEvent.query.filter_by(is_published=True).count(),
    }
    return render_template(
        "admin/dashboard.html",
        active_view=active_view,
        stats=stats,
        user_rows=user_rows,
        pending_trends=pending_trends,
        published_trends=published_trends,
        active_tab=active_tab,
        active_trends=active_trends,
        selected_trend=selected_trend,
        pending_questions=pending_questions,
        search=search,
    )