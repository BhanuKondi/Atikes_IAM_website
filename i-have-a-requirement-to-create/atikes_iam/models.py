from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(160), default="IAM Community Member")
    company = db.Column(db.String(160), default="")
    bio = db.Column(db.Text, default="")
    role = db.Column(db.String(30), default="user", index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    questions = db.relationship(
        "Question",
        back_populates="author",
        lazy="dynamic",
        foreign_keys="Question.author_id",
    )
    answers = db.relationship(
        "Answer",
        back_populates="author",
        lazy="dynamic",
        foreign_keys="Answer.author_id",
    )
    expert_profile = db.relationship(
        "ExpertProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def answer_count(self):
        return self.answers.filter_by(status="approved").count()

    @property
    def is_admin(self):
        return self.role == "admin"


class TrendSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, unique=True)
    feed_url = db.Column(db.String(500), nullable=False, unique=True)
    website_url = db.Column(db.String(500), default="")
    category = db.Column(db.String(120), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    last_fetched_at = db.Column(db.DateTime(timezone=True))
    last_error = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    trends = db.relationship("Trend", back_populates="source", lazy="dynamic")


class Trend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    summary = db.Column(db.Text, default="")
    generated_content = db.Column(db.Text, default="")
    image_url = db.Column(db.String(700), default="")
    image_path = db.Column(db.String(500), default="")
    url = db.Column(db.String(700), nullable=False, unique=True, index=True)
    source_domain = db.Column(db.String(180), default="")
    category = db.Column(db.String(120), nullable=False, index=True)
    score = db.Column(db.Integer, default=0, index=True)
    published_at = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)
    fetched_at = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)
    status = db.Column(db.String(30), default="pending", index=True)
    approved_at = db.Column(db.DateTime(timezone=True))
    approved_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    source_id = db.Column(db.Integer, db.ForeignKey("trend_source.id"), nullable=False)

    source = db.relationship("TrendSource", back_populates="trends")
    approved_by = db.relationship("User", foreign_keys=[approved_by_id])


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(220), nullable=False)
    body = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), default="")
    version = db.Column(db.String(80), default="")
    attachment_filename = db.Column(db.String(255), default="")
    attachment_path = db.Column(db.String(500), default="")
    status = db.Column(db.String(30), default="pending", index=True)
    approved_at = db.Column(db.DateTime(timezone=True))
    approved_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    author = db.relationship("User", back_populates="questions", foreign_keys=[author_id])
    approved_by = db.relationship("User", foreign_keys=[approved_by_id])
    answers = db.relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    attachments = db.relationship(
        "QuestionAttachment",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @property
    def approved_answer_count(self):
        return self.answers.filter_by(status="approved").count()


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="pending", index=True)
    approved_at = db.Column(db.DateTime(timezone=True))
    approved_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)

    author = db.relationship("User", back_populates="answers", foreign_keys=[author_id])
    approved_by = db.relationship("User", foreign_keys=[approved_by_id])
    question = db.relationship("Question", back_populates="answers")


class QuestionAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    question = db.relationship("Question", back_populates="attachments")


class ExpertProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    display_name = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(160), default="IAM Community Expert")
    company = db.Column(db.String(160), default="")
    bio = db.Column(db.Text, default="")
    answer_total = db.Column(db.Integer, default=0, index=True)
    question_total = db.Column(db.Integer, default=0)
    is_listed = db.Column(db.Boolean, default=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = db.relationship("User", back_populates="expert_profile")


class UpcomingEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(220), nullable=False)
    description = db.Column(db.Text, default="")
    event_type = db.Column(db.String(80), default="Webinar", index=True)
    organizer = db.Column(db.String(160), default="")
    location = db.Column(db.String(180), default="Online")
    starts_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    ends_at = db.Column(db.DateTime(timezone=True))
    registration_url = db.Column(db.String(700), default="")
    source_url = db.Column(db.String(700), default="")
    is_published = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)
