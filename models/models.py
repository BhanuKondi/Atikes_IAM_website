from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from models.db import db


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
    points = db.Column(db.Integer, default=0)
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
    saved_questions = db.relationship(
        "SavedQuestion",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
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
    logs = db.Column(db.Text, default="")
    has_logs = db.Column(db.Boolean, default=False, index=True)
    tags = db.Column(db.String(255), default="")
    version = db.Column(db.String(80), default="")
    difficulty = db.Column(db.String(30), default="Beginner", index=True)
    views_count = db.Column(db.Integer, default=0, index=True)
    attachment_filename = db.Column(db.String(255), default="")
    attachment_path = db.Column(db.String(500), default="")
    status = db.Column(db.String(30), default="pending", index=True)
    rejection_reason = db.Column(db.Text, default="")
    approved_at = db.Column(db.DateTime(timezone=True))
    approved_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    solution_answer_id = db.Column(db.Integer, db.ForeignKey("answer.id"))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id"), index=True)
    version_id = db.Column(db.Integer, db.ForeignKey("product_version.id"), index=True)

    author = db.relationship("User", back_populates="questions", foreign_keys=[author_id])
    approved_by = db.relationship("User", foreign_keys=[approved_by_id])
    product = db.relationship("Product", back_populates="questions")
    topic = db.relationship("Topic", back_populates="questions")
    product_version = db.relationship("ProductVersion")
    solution_answer = db.relationship("Answer", foreign_keys=[solution_answer_id], post_update=True)
    answers = db.relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="dynamic",
        foreign_keys="Answer.question_id",
    )
    attachments = db.relationship(
        "QuestionAttachment",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    reactions = db.relationship(
        "QuestionReaction",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    views = db.relationship(
        "QuestionView",
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
    question = db.relationship("Question", back_populates="answers", foreign_keys=[question_id])
    reactions = db.relationship(
        "AnswerReaction",
        back_populates="answer",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    comments = db.relationship(
        "AnswerComment",
        back_populates="answer",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    attachments = db.relationship(
        "AnswerAttachment",
        back_populates="answer",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )


class AnswerReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reaction_type = db.Column(db.String(20), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)
    answer_id = db.Column(db.Integer, db.ForeignKey("answer.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    answer = db.relationship("Answer", back_populates="reactions")
    user = db.relationship("User")

    __table_args__ = (db.UniqueConstraint("answer_id", "user_id", "reaction_type", name="uq_answer_reaction_user_type"),)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, unique=True, index=True)
    slug = db.Column(db.String(180), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    versions = db.relationship(
        "ProductVersion",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    topics = db.relationship(
        "Topic",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    questions = db.relationship("Question", back_populates="product", lazy="dynamic")


class ProductVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(120), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    product = db.relationship("Product", back_populates="versions")

    __table_args__ = (db.UniqueConstraint("product_id", "label", name="uq_product_version_label"),)


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    product = db.relationship("Product", back_populates="topics")
    questions = db.relationship("Question", back_populates="topic", lazy="dynamic")

    __table_args__ = (db.UniqueConstraint("product_id", "name", name="uq_product_topic_name"),)


class QuestionReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reaction_type = db.Column(db.String(20), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    question = db.relationship("Question", back_populates="reactions")
    user = db.relationship("User")

    __table_args__ = (db.UniqueConstraint("question_id", "user_id", "reaction_type", name="uq_question_reaction_user_type"),)


class QuestionView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    session_id = db.Column(db.String(120), default="", index=True)

    question = db.relationship("Question", back_populates="views")
    user = db.relationship("User")


class SavedQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False, index=True)

    user = db.relationship("User", back_populates="saved_questions")
    question = db.relationship("Question")

    __table_args__ = (db.UniqueConstraint("user_id", "question_id", name="uq_saved_question_user"),)


class AnswerComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)
    answer_id = db.Column(db.Integer, db.ForeignKey("answer.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    answer = db.relationship("Answer", back_populates="comments")
    user = db.relationship("User")


class QuestionAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_hash = db.Column(db.String(64), default="", index=True)
    uploaded_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    question = db.relationship("Question", back_populates="attachments")

    __table_args__ = (db.UniqueConstraint("question_id", "filename", name="uq_question_attachment_filename"),)


class AnswerAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey("answer.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_hash = db.Column(db.String(64), default="", index=True)
    uploaded_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    answer = db.relationship("Answer", back_populates="attachments")

    __table_args__ = (db.UniqueConstraint("answer_id", "filename", name="uq_answer_attachment_filename"),)


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
