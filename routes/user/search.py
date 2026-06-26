from flask import Blueprint, render_template, request
from flask_login import login_required

from models import ExpertProfile, Question, Trend, UpcomingEvent


search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.route("/")
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
        "user/search/search.html",
        query=query,
        trends=trends,
        questions=questions,
        experts=experts,
        events=events,
    )