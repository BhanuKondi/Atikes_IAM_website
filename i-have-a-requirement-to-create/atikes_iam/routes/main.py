from flask import Blueprint, render_template

from ..models import Answer, ExpertProfile, Question, Trend, UpcomingEvent
from ..services.trends import fetch_live_trends


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    trends, trend_errors, refreshed = fetch_live_trends()
    questions = Question.query.filter_by(status="approved").order_by(Question.created_at.desc()).limit(5).all()
    experts = ExpertProfile.query.filter_by(is_listed=True).order_by(
        ExpertProfile.answer_total.desc(),
        ExpertProfile.updated_at.desc(),
    ).limit(5).all()
    events = (
        UpcomingEvent.query.filter_by(is_published=True)
        .order_by(UpcomingEvent.starts_at.asc())
        .limit(4)
        .all()
    )
    stats = {
        "trends": Trend.query.filter_by(status="approved").count(),
        "questions": Question.query.filter_by(status="approved").count(),
        "answers": Answer.query.filter_by(status="approved").count(),
        "experts": ExpertProfile.query.filter_by(is_listed=True).count(),
    }
    return render_template(
        "home.html",
        trends=trends[:5],
        trend_errors=trend_errors,
        refreshed=refreshed,
        questions=questions,
        experts=experts,
        events=events,
        stats=stats,
    )
