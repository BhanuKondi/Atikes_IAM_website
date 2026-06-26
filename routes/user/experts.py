from flask import Blueprint, render_template
from models import ExpertProfile


experts_bp = Blueprint("experts", __name__, url_prefix="/experts")


@experts_bp.route("/")
def directory():
    experts = (
        ExpertProfile.query.filter_by(is_listed=True)
        .order_by(ExpertProfile.answer_total.desc(), ExpertProfile.updated_at.desc())
        .all()
    )
    return render_template(
        "user/experts/experts.html",
        top_experts=experts[:3],
        remaining_experts=experts[3:],
    )
