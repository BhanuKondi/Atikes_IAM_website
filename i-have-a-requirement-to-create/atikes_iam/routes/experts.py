from flask import Blueprint, render_template
from sqlalchemy import func

from ..extensions import db
from ..models import Answer, User


experts_bp = Blueprint("experts", __name__, url_prefix="/experts")


@experts_bp.route("/")
def directory():
    experts = (
        db.session.query(User, func.count(Answer.id).label("answer_total"))
        .join(Answer, Answer.author_id == User.id)
        .group_by(User.id)
        .order_by(func.count(Answer.id).desc(), User.created_at.asc())
        .all()
    )
    return render_template("experts.html", experts=experts)
