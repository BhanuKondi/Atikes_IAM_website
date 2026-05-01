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
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    questions = db.relationship("Question", back_populates="author", lazy="dynamic")
    answers = db.relationship("Answer", back_populates="author", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def answer_count(self):
        return self.answers.count()


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(220), nullable=False)
    body = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    author = db.relationship("User", back_populates="questions")
    answers = db.relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)

    author = db.relationship("User", back_populates="answers")
    question = db.relationship("Question", back_populates="answers")
