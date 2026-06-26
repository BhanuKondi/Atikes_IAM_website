from functools import wraps

from flask import abort
from flask_login import current_user, login_required

from models import utcnow
from models.db import db
from utils.experts import refresh_expert_profile


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def approve_trend_record(trend):
    if trend.generated_content:
        trend.summary = trend.generated_content
    trend.status = "approved"
    trend.approved_at = utcnow()
    trend.approved_by = current_user
    db.session.commit()


def approve_question_record(question):
    question.status = "approved"
    question.approved_at = utcnow()
    question.approved_by = current_user
    refresh_expert_profile(question.author)
    db.session.commit()