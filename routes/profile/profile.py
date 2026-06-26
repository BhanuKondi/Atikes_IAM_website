from flask import Blueprint, render_template
from flask_login import current_user, login_required

from models import Answer, Question, SavedQuestion


profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/")
@login_required
def profile():
    approved_questions = Question.query.filter_by(author_id=current_user.id, status="approved").count()
    pending_questions = Question.query.filter_by(author_id=current_user.id, status="pending").count()
    approved_answers = Answer.query.filter_by(author_id=current_user.id, status="approved").count()
    pending_answers = Answer.query.filter_by(author_id=current_user.id, status="pending").count()
    user_questions = Question.query.filter_by(author_id=current_user.id).order_by(Question.created_at.desc()).all()
    saved_questions = (
        SavedQuestion.query.filter_by(user_id=current_user.id)
        .order_by(SavedQuestion.created_at.desc())
        .all()
    )
    points = current_user.points or 0
    notifications = []
    if pending_questions:
        notifications.append(f"{pending_questions} question(s) waiting for admin review.")
    if pending_answers:
        notifications.append(f"{pending_answers} answer(s) waiting for admin review.")
    if not notifications:
        notifications.append("No pending notifications.")
    return render_template(
        "profile/profile.html",
        points=points,
        approved_questions=approved_questions,
        approved_answers=approved_answers,
        pending_questions=pending_questions,
        pending_answers=pending_answers,
        user_questions=user_questions,
        saved_questions=saved_questions,
        notifications=notifications,
    )
