from flask import Blueprint, render_template
from flask_login import login_required
from ..models import ExpertProfile


experts_bp = Blueprint("experts", __name__, url_prefix="/experts")


@experts_bp.route("/")
@login_required
def directory():
    experts = (
        ExpertProfile.query.filter_by(is_listed=True)
        .order_by(ExpertProfile.answer_total.desc(), ExpertProfile.updated_at.desc())
        .all()
    )
    return render_template(
        "experts.html",
        top_experts=experts[:3],
        remaining_experts=experts[3:],
    )
