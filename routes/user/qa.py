import hashlib
import re
import uuid
from pathlib import Path

from flask import Blueprint, abort, current_app, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from werkzeug.utils import secure_filename

from models import (
    Answer,
    AnswerAttachment,
    AnswerComment,
    AnswerReaction,
    Product,
    ProductVersion,
    Question,
    QuestionAttachment,
    QuestionReaction,
    QuestionView,
    SavedQuestion,
    Topic,
    utcnow,
)
from models.db import db
from utils.experts import refresh_expert_profile


qa_bp = Blueprint("qa", __name__, url_prefix="/qa")

ALLOWED_ATTACHMENTS = {"pdf", "jpg", "jpeg", "png", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv", "zip"}
INLINE_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
DIFFICULTY_OPTIONS = ["Beginner", "Intermediate", "Advanced"]
REACTION_CHOICES = (
    ("love", "❤️", "Like"),
    ("thumbs_up", "👍", "Thumbs Up"),
    ("wow", "😮", "Wow"),
    ("clap", "👏", "Clap"),
    ("celebrate", "🎉", "Celebrate"),
)
SOLUTION_POINTS = 50


def _wants_json():
    return request.accept_mimetypes.best == "application/json" or request.headers.get("X-Requested-With") == "fetch"


def _days_ago(value):
    if not value:
        return ""
    now = utcnow()
    if value.tzinfo is None and now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    delta = now - value
    if delta.days <= 0:
        return "today"
    if delta.days == 1:
        return "1 day ago"
    return f"{delta.days} days ago"


def _exact_timestamp(value):
    if not value:
        return ""
    return value.strftime("%d %b %Y, %I:%M %p")


def _viewer_key():
    if current_user.is_authenticated:
        return current_user.id, f"user:{current_user.id}"
    session.setdefault("qa_viewer_id", uuid.uuid4().hex)
    return None, session["qa_viewer_id"]


def _award_points(user, points):
    if user and points:
        user.points = (user.points or 0) + points


def _tag_values(question):
    old_tags = [tag.strip() for tag in (question.tags or "").split(",") if tag.strip()]
    product = question.product.name if question.product else (old_tags[0] if old_tags else "")
    topic = question.topic.name if question.topic else (old_tags[1] if len(old_tags) > 1 else "")
    version = question.product_version.label if question.product_version else question.version
    return {
        "product": product,
        "topic": topic,
        "version": version,
        "difficulty": question.difficulty or (old_tags[2] if len(old_tags) > 2 else "Beginner"),
    }


def _reaction_summary(target, reaction_model, foreign_key):
    reactions = reaction_model.query.filter(getattr(reaction_model, foreign_key) == target.id).all()
    summary = {
        key: {"symbol": symbol, "label": label, "count": 0, "selected": False}
        for key, symbol, label in REACTION_CHOICES
    }
    for reaction in reactions:
        bucket = summary.get(reaction.reaction_type)
        if not bucket:
            continue
        bucket["count"] += 1
        bucket["selected"] = bucket["selected"] or (
            current_user.is_authenticated and reaction.user_id == current_user.id
        )
    return summary


def _attachment_payload(attachment):
    extension = attachment.filename.rsplit(".", 1)[-1].lower() if "." in attachment.filename else ""
    return {
        "id": attachment.id,
        "filename": attachment.filename,
        "url": url_for("static", filename=attachment.file_path),
        "is_image": extension in INLINE_IMAGE_EXTENSIONS,
    }


def _answer_payload(answer):
    return {
        "id": answer.id,
        "content": answer.body,
        "author": answer.author.name,
        "author_tag": "",
        "created": _exact_timestamp(answer.created_at),
        "attachments": [_attachment_payload(item) for item in answer.attachments.order_by(AnswerAttachment.uploaded_at.asc()).all()],
        "reactions": _reaction_summary(answer, AnswerReaction, "answer_id"),
        "comments": [
            {"id": comment.id, "author": comment.user.name, "content": comment.body, "created": _exact_timestamp(comment.created_at)}
            for comment in answer.comments.order_by(AnswerComment.created_at.asc()).all()
        ],
    }


def _question_payload(question, detail=False):
    tags = _tag_values(question)
    answers_query = question.answers.filter_by(status="approved")
    answer_count = answers_query.count()
    payload = {
        "id": question.id,
        "title": question.title,
        "description": question.body,
        "logs": question.logs if question.has_logs else "",
        "has_logs": bool(question.has_logs and question.logs),
        "status": question.status,
        "rejection_reason": question.rejection_reason or "",
        "author": question.author.name,
        "created": _days_ago(question.created_at),
        "created_full": question.created_at.strftime("%b %d, %Y"),
        "views": question.views_count or 0,
        "answers_count": answer_count,
        "solution_answer_id": question.solution_answer_id,
        "has_solution": bool(question.solution_answer_id),
        "can_mark_solution": current_user.is_authenticated and current_user.id == question.author_id,
        "can_admin": current_user.is_authenticated and current_user.is_admin,
        "is_saved": current_user.is_authenticated and SavedQuestion.query.filter_by(user_id=current_user.id, question_id=question.id).first() is not None,
        "tags": tags,
        "attachments": [_attachment_payload(item) for item in question.attachments.order_by(QuestionAttachment.uploaded_at.asc()).all()],
        "reactions": _reaction_summary(question, QuestionReaction, "question_id"),
        "url": url_for("qa.question_detail", question_id=question.id, _external=True),
    }
    if detail:
        answers = answers_query.order_by(Answer.created_at.asc()).all()
        if question.solution_answer_id:
            answers.sort(key=lambda answer: 0 if answer.id == question.solution_answer_id else 1)
        payload["answers"] = [_answer_payload(answer) for answer in answers]
    return payload


def _question_query():
    is_admin = current_user.is_authenticated and current_user.is_admin
    status = request.args.get("status", "approved")
    if status not in {"approved", "pending", "rejected"}:
        status = "approved"
    if status != "approved" and not is_admin:
        status = "approved"
    query = Question.query.filter_by(status=status)

    product_id = request.args.get("product_id", type=int)
    topic_id = request.args.get("topic_id", type=int)
    search = request.args.get("q", "").strip()
    solved = request.args.get("filter", "all")
    if product_id:
        query = query.filter_by(product_id=product_id)
    if topic_id:
        query = query.filter_by(topic_id=topic_id)
    if solved == "solved":
        query = query.filter(Question.solution_answer_id.isnot(None))
    elif solved == "unsolved":
        query = query.filter(Question.solution_answer_id.is_(None))
    if search:
        pattern = f"%{search}%"
        query = query.filter(Question.title.ilike(pattern) | Question.body.ilike(pattern))
    return query.order_by(Question.created_at.desc())


def _file_hash(upload):
    digest = hashlib.sha256()
    while True:
        chunk = upload.stream.read(1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
    upload.stream.seek(0)
    return digest.hexdigest()


def _save_attachments(owner, uploads, folder, attachment_model, owner_attr):
    upload_dir = Path(current_app.root_path) / "static" / "uploads" / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    seen_names = set()
    seen_hashes = set()
    existing = getattr(owner, "attachments").all()
    existing_names = {item.filename.lower() for item in existing}
    existing_hashes = {item.file_hash for item in existing if item.file_hash}
    for upload in uploads:
        if not upload or not upload.filename:
            continue
        filename = secure_filename(upload.filename)
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if extension not in ALLOWED_ATTACHMENTS:
            continue
        digest = _file_hash(upload)
        if filename.lower() in seen_names or filename.lower() in existing_names or digest in seen_hashes or digest in existing_hashes:
            continue
        seen_names.add(filename.lower())
        seen_hashes.add(digest)
        stored_name = f"{folder}-{owner.id}-{uuid.uuid4().hex[:10]}-{filename}"
        upload.save(upload_dir / stored_name)
        attachment = attachment_model(
            **{
                owner_attr: owner,
                "filename": filename,
                "file_path": f"uploads/{folder}/{stored_name}",
                "file_hash": digest,
            }
        )
        db.session.add(attachment)
        saved.append(attachment)
    return saved


def _sync_question_tags(question):
    tags = _tag_values(question)
    question.version = tags["version"] or question.version or ""
    question.tags = ", ".join(value for value in [tags["product"], tags["topic"], tags["difficulty"]] if value)


def _product_slug(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or uuid.uuid4().hex[:10]


def _get_or_create_product(product_id, new_product):
    product = Product.query.get(product_id) if product_id else None
    if not product:
        return None
    if product.slug != "other":
        return product
    product_name = (new_product or "").strip()
    if not product_name:
        return product
    existing = Product.query.filter(func.lower(Product.name) == product_name.lower()).first()
    if existing:
        return existing
    base_slug = _product_slug(product_name)
    slug = base_slug
    counter = 2
    while Product.query.filter_by(slug=slug).first() is not None:
        slug = f"{base_slug}-{counter}"
        counter += 1
    created = Product(name=product_name, slug=slug)
    db.session.add(created)
    db.session.flush()
    return created


def _get_or_create_topic(product, topic_id, new_topic):
    if new_topic:
        topic = Topic.query.filter(func.lower(Topic.name) == new_topic.lower(), Topic.product_id == product.id).first()
        if topic is None:
            topic = Topic(product=product, name=new_topic.strip())
            db.session.add(topic)
            db.session.flush()
        return topic
    return Topic.query.filter_by(id=topic_id, product_id=product.id).first()


def _get_or_create_version(product, version_id, new_version):
    if not product:
        return None
    product_name = (product.name or "").lower().replace(" ", "")
    is_iiq = product_name in {"identityiq", "iiq"} or "identityiq" in product_name
    if not is_iiq:
        return None
    if new_version:
        label = new_version.strip()
        version = ProductVersion.query.filter(
            func.lower(ProductVersion.label) == label.lower(),
            ProductVersion.product_id == product.id,
        ).first()
        if version is None:
            version = ProductVersion(product=product, label=label)
            db.session.add(version)
            db.session.flush()
        return version
    return ProductVersion.query.filter_by(id=version_id, product_id=product.id).first()


@qa_bp.get("/")
def questions():
    products = Product.query.order_by(Product.name.asc()).all()
    approved_total = Question.query.filter_by(status="approved").count()
    return render_template(
        "user/qa/list.html",
        products=products,
        approved_total=approved_total,
        difficulty_options=DIFFICULTY_OPTIONS,
        reaction_choices=REACTION_CHOICES,
        initial_questions=[_question_payload(question) for question in _question_query().all()],
        active_status=request.args.get("status", "approved"),
    )


@qa_bp.route("/ask", methods=["GET", "POST"])
@login_required
def ask_question():
    if request.method == "GET":
        return redirect(url_for("qa.questions"))
    return create_question()


@qa_bp.route("/<int:question_id>", methods=["GET", "POST"])
def question_detail(question_id):
    if request.method == "POST":
        return create_answer(question_id)
    return redirect(url_for("qa.questions", question_id=question_id))


@qa_bp.get("/api/products")
def api_products():
    products = Product.query.order_by(Product.name.asc()).all()
    return jsonify(
        {
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "slug": product.slug,
                    "versions": [{"id": version.id, "label": version.label} for version in product.versions.order_by(ProductVersion.label.asc()).all()],
                    "topics": [
                        {
                            "id": topic.id,
                            "name": topic.name,
                            "count": topic.questions.filter_by(status="approved").count(),
                        }
                        for topic in product.topics.order_by(Topic.name.asc()).all()
                    ],
                    "count": product.questions.filter_by(status="approved").count(),
                }
                for product in products
            ],
            "difficulties": DIFFICULTY_OPTIONS,
        }
    )


@qa_bp.get("/api/questions")
def api_questions():
    return jsonify({"questions": [_question_payload(question) for question in _question_query().all()]})


@qa_bp.get("/api/questions/<int:question_id>")
def api_question_detail(question_id):
    question = Question.query.get_or_404(question_id)
    can_view_pending = current_user.is_authenticated and (current_user.is_admin or current_user.id == question.author_id)
    if question.status != "approved" and not can_view_pending:
        abort(404)
    if question.status == "approved":
        user_id, session_id = _viewer_key()
        view_query = QuestionView.query.filter_by(question_id=question.id)
        view_query = view_query.filter_by(user_id=user_id) if user_id else view_query.filter_by(session_id=session_id)
        if view_query.first() is None:
            db.session.add(QuestionView(question=question, user_id=user_id, session_id=session_id))
            question.views_count = (question.views_count or 0) + 1
            db.session.commit()
    return jsonify({"question": _question_payload(question, detail=True)})


@qa_bp.post("/api/questions")
@login_required
def create_question():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", request.form.get("body", "")).strip()
    product = _get_or_create_product(
        request.form.get("product_id", type=int),
        request.form.get("new_product", "").strip(),
    )
    version = _get_or_create_version(
        product,
        request.form.get("version_id", type=int),
        request.form.get("new_version", "").strip(),
    )
    topic = _get_or_create_topic(product, request.form.get("topic_id", type=int), request.form.get("new_topic", "").strip()) if product else None
    difficulty = request.form.get("difficulty", "Beginner").strip()
    has_logs = request.form.get("has_logs", request.form.get("wants_error_logs", "No")) == "Yes"
    logs = request.form.get("logs", request.form.get("error_logs", "")).strip() if has_logs else ""

    if product and product.slug == "other" and not request.form.get("new_product", "").strip():
        return jsonify({"ok": False, "message": "Please enter the product name."}), 400
    if not product or not topic or difficulty not in DIFFICULTY_OPTIONS:
        return jsonify({"ok": False, "message": "Please choose a product, topic, and difficulty."}), 400
    if len(title) < 10 or len(description) < 20:
        return jsonify({"ok": False, "message": "Please add a clear title and useful description."}), 400
    if has_logs and not logs:
        return jsonify({"ok": False, "message": "Paste logs or choose No."}), 400

    question = Question(
        title=title,
        body=description,
        logs=logs,
        has_logs=bool(logs),
        product=product,
        product_version=version,
        topic=topic,
        difficulty=difficulty,
        status="pending",
        rejection_reason="",
        author=current_user,
    )
    _sync_question_tags(question)
    db.session.add(question)
    db.session.flush()
    saved = _save_attachments(question, request.files.getlist("attachments"), "questions", QuestionAttachment, "question")
    if saved:
        question.attachment_filename = saved[0].filename
        question.attachment_path = saved[0].file_path
    refresh_expert_profile(current_user)
    db.session.commit()
    return jsonify({"ok": True, "message": "Your question is under review and is pending approval", "question": _question_payload(question)})


@qa_bp.post("/api/questions/<int:question_id>/answers")
@login_required
def create_answer(question_id):
    question = Question.query.filter_by(id=question_id, status="approved").first_or_404()
    content = request.form.get("content", request.form.get("problem_statement", request.form.get("body", ""))).strip()
    if len(content) < 3:
        return jsonify({"ok": False, "message": "Please write a reply before posting."}), 400
    answer = Answer(body=content, author=current_user, question=question, status="approved", approved_at=utcnow(), approved_by=current_user)
    db.session.add(answer)
    db.session.flush()
    _save_attachments(answer, request.files.getlist("attachments"), "answers", AnswerAttachment, "answer")
    _award_points(current_user, 3)
    refresh_expert_profile(current_user)
    db.session.commit()
    return jsonify({"ok": True, "answer": _answer_payload(answer), "question": _question_payload(question, detail=True)})


def _toggle_reaction(target, reaction_model, relation_name, reaction_type):
    if reaction_type not in {choice[0] for choice in REACTION_CHOICES}:
        abort(400)
    relation_id = f"{relation_name}_id"
    reaction = reaction_model.query.filter_by(**{relation_id: target.id, "user_id": current_user.id, "reaction_type": reaction_type}).first()
    selected = False
    if reaction:
        db.session.delete(reaction)
    else:
        db.session.add(reaction_model(**{relation_name: target, "user": current_user, "reaction_type": reaction_type}))
        selected = True
    db.session.commit()
    return selected


@qa_bp.post("/api/questions/<int:question_id>/reactions")
@login_required
def react_to_question_api(question_id):
    question = Question.query.filter_by(id=question_id, status="approved").first_or_404()
    _toggle_reaction(question, QuestionReaction, "question", request.form.get("reaction_type", ""))
    return jsonify({"ok": True, "reactions": _reaction_summary(question, QuestionReaction, "question_id")})


@qa_bp.post("/api/answers/<int:answer_id>/reactions")
@login_required
def react_to_answer_api(answer_id):
    answer = Answer.query.filter_by(id=answer_id, status="approved").first_or_404()
    _toggle_reaction(answer, AnswerReaction, "answer", request.form.get("reaction_type", ""))
    return jsonify({"ok": True, "reactions": _reaction_summary(answer, AnswerReaction, "answer_id")})


@qa_bp.post("/api/questions/<int:question_id>/save")
@login_required
def save_question_api(question_id):
    question = Question.query.filter_by(id=question_id, status="approved").first_or_404()
    saved = SavedQuestion.query.filter_by(user_id=current_user.id, question_id=question.id).first()
    if saved:
        db.session.delete(saved)
        is_saved = False
    else:
        db.session.add(SavedQuestion(user=current_user, question=question))
        is_saved = True
    db.session.commit()
    return jsonify({"ok": True, "saved": is_saved})


@qa_bp.post("/api/answers/<int:answer_id>/solution")
@login_required
def mark_solution_api(answer_id):
    answer = Answer.query.filter_by(id=answer_id, status="approved").first_or_404()
    question = answer.question
    if question.author_id != current_user.id:
        abort(403)
    previous_solution = question.solution_answer
    if question.solution_answer_id == answer.id:
        question.solution_answer_id = None
        _award_points(answer.author, -SOLUTION_POINTS)
    else:
        if previous_solution is not None:
            _award_points(previous_solution.author, -SOLUTION_POINTS)
        question.solution_answer_id = answer.id
        _award_points(answer.author, SOLUTION_POINTS)
    db.session.commit()
    return jsonify({"ok": True, "question": _question_payload(question, detail=True)})


@qa_bp.post("/api/admin/questions/<int:question_id>/approve")
@login_required
def approve_question_api(question_id):
    if not current_user.is_admin:
        abort(403)
    question = Question.query.get_or_404(question_id)
    question.status = "approved"
    question.rejection_reason = ""
    question.approved_at = utcnow()
    question.approved_by = current_user
    refresh_expert_profile(question.author)
    db.session.commit()
    return jsonify({"ok": True, "question": _question_payload(question)})


@qa_bp.post("/api/admin/questions/<int:question_id>/reject")
@login_required
def reject_question_api(question_id):
    if not current_user.is_admin:
        abort(403)
    question = Question.query.get_or_404(question_id)
    reason = request.form.get("reason", "").strip()
    if not reason:
        return jsonify({"ok": False, "message": "Please add a rejection reason."}), 400
    question.status = "rejected"
    question.rejection_reason = reason
    question.approved_at = None
    question.approved_by = None
    db.session.commit()
    return jsonify({"ok": True})


@qa_bp.post("/<int:question_id>/save")
@login_required
def save_question(question_id):
    if _wants_json():
        return save_question_api(question_id)
    save_question_api(question_id)
    return redirect(request.form.get("next") or url_for("qa.questions", question_id=question_id))


@qa_bp.post("/answers/<int:answer_id>/react")
@login_required
def react_to_answer(answer_id):
    if _wants_json():
        return react_to_answer_api(answer_id)
    react_to_answer_api(answer_id)
    answer = Answer.query.get_or_404(answer_id)
    return redirect(request.form.get("next") or url_for("qa.questions", question_id=answer.question_id))


@qa_bp.post("/answers/<int:answer_id>/comment")
@login_required
def comment_on_answer(answer_id):
    answer = Answer.query.filter_by(id=answer_id, status="approved").first_or_404()
    body = request.form.get("body", "").strip()
    if len(body) < 2:
        return jsonify({"ok": False, "message": "Please write a comment before posting."}), 400
    db.session.add(AnswerComment(answer=answer, user=current_user, body=body))
    db.session.commit()
    return jsonify({"ok": True, "answer": _answer_payload(answer)})


@qa_bp.post("/answers/<int:answer_id>/solution")
@login_required
def mark_solution(answer_id):
    if _wants_json():
        return mark_solution_api(answer_id)
    mark_solution_api(answer_id)
    answer = Answer.query.get_or_404(answer_id)
    return redirect(request.form.get("next") or url_for("qa.questions", question_id=answer.question_id))
