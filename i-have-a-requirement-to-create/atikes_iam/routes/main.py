from flask import Blueprint, render_template

from ..models import Answer, Question, User
from ..services.trends import fetch_live_trends


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    trends, trend_errors, refreshed = fetch_live_trends()
    questions = Question.query.order_by(Question.created_at.desc()).limit(5).all()
    experts = (
        User.query.join(Answer)
        .group_by(User.id)
        .order_by(db_text("count(answer.id) desc"))
        .limit(5)
        .all()
    )
    stats = {
        "trends": len(trends),
        "questions": Question.query.count(),
        "answers": Answer.query.count(),
        "experts": len(experts),
    }
    return render_template(
        "home.html",
        trends=trends[:5],
        trend_errors=trend_errors,
        refreshed=refreshed,
        questions=questions,
        experts=experts,
        stats=stats,
    )


def db_text(sql):
    from sqlalchemy import text

    return text(sql)
