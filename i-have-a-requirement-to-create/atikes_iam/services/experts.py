from ..extensions import db
from ..models import Answer, ExpertProfile, Question


def refresh_expert_profile(user):
    profile = user.expert_profile
    if profile is None:
        profile = ExpertProfile(user=user, display_name=user.name)
        db.session.add(profile)

    profile.display_name = user.name
    profile.title = user.title
    profile.company = user.company
    profile.bio = user.bio
    profile.answer_total = Answer.query.filter_by(author_id=user.id).count()
    profile.question_total = Question.query.filter_by(author_id=user.id).count()
    profile.is_listed = profile.answer_total > 0
    return profile
