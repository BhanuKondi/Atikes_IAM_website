from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from ..models import Answer, ExpertProfile, Question, Trend, UpcomingEvent
from ..services.trends import fetch_live_trends


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    trends, trend_errors, refreshed = fetch_live_trends()
    questions = Question.query.filter_by(status="approved").order_by(Question.created_at.desc()).limit(5).all()
    experts = (
        ExpertProfile.query.filter_by(is_listed=True)
        .order_by(ExpertProfile.answer_total.desc(), ExpertProfile.updated_at.desc())
        .limit(5)
        .all()
    )
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


@main_bp.route("/profile")
@login_required
def profile():
    approved_questions = Question.query.filter_by(author_id=current_user.id, status="approved").count()
    pending_questions = Question.query.filter_by(author_id=current_user.id, status="pending").count()
    approved_answers = Answer.query.filter_by(author_id=current_user.id, status="approved").count()
    pending_answers = Answer.query.filter_by(author_id=current_user.id, status="pending").count()
    points = approved_answers * 10 + approved_questions * 2
    notifications = []
    if pending_questions:
        notifications.append(f"{pending_questions} question(s) waiting for admin review.")
    if pending_answers:
        notifications.append(f"{pending_answers} answer(s) waiting for admin review.")
    if not notifications:
        notifications.append("No pending notifications.")
    return render_template(
        "profile.html",
        points=points,
        approved_questions=approved_questions,
        approved_answers=approved_answers,
        notifications=notifications,
    )


@main_bp.route("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()
    pattern = f"%{query}%"
    trends = []
    questions = []
    experts = []
    events = []
    if query:
        trends = Trend.query.filter(
            Trend.status == "approved",
            Trend.title.ilike(pattern) | Trend.summary.ilike(pattern) | Trend.generated_content.ilike(pattern),
        ).limit(10).all()
        questions = Question.query.filter(
            Question.status == "approved",
            Question.title.ilike(pattern) | Question.body.ilike(pattern) | Question.tags.ilike(pattern),
        ).limit(10).all()
        experts = ExpertProfile.query.filter(
            ExpertProfile.is_listed.is_(True),
            ExpertProfile.display_name.ilike(pattern) | ExpertProfile.title.ilike(pattern) | ExpertProfile.bio.ilike(pattern),
        ).limit(10).all()
        events = UpcomingEvent.query.filter(
            UpcomingEvent.is_published.is_(True),
            UpcomingEvent.title.ilike(pattern) | UpcomingEvent.description.ilike(pattern) | UpcomingEvent.organizer.ilike(pattern),
        ).limit(10).all()
    return render_template(
        "search.html",
        query=query,
        trends=trends,
        questions=questions,
        experts=experts,
        events=events,
    )
