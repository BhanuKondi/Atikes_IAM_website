from pathlib import Path

from flask import Flask
from sqlalchemy import inspect, text

from instance.config import Config
from models import Product, ProductVersion, Topic, User, db, login_manager
from utils.bootstrap import sync_trend_sources


def _ensure_schema_updates(app):
    inspector = inspect(db.engine)
    if not inspector.has_table("question"):
        return

    question_columns = {column["name"] for column in inspector.get_columns("question")}
    question_additions = {
        "solution_answer_id": "INT NULL",
        "logs": "TEXT",
        "has_logs": "BOOLEAN DEFAULT 0",
        "difficulty": "VARCHAR(30) DEFAULT 'Beginner'",
        "views_count": "INT DEFAULT 0",
        "product_id": "INT NULL",
        "topic_id": "INT NULL",
        "version_id": "INT NULL",
        "rejection_reason": "TEXT",
    }
    for column_name, definition in question_additions.items():
        if column_name not in question_columns:
            db.session.execute(text(f"ALTER TABLE question ADD COLUMN {column_name} {definition}"))
            if db.engine.dialect.name == "mysql" and column_name.endswith("_id"):
                db.session.execute(text(f"CREATE INDEX ix_question_{column_name} ON question ({column_name})"))
            db.session.commit()

    attachment_columns = set()
    if inspector.has_table("question_attachment"):
        attachment_columns = {column["name"] for column in inspector.get_columns("question_attachment")}
    if "file_hash" not in attachment_columns and inspector.has_table("question_attachment"):
        db.session.execute(text("ALTER TABLE question_attachment ADD COLUMN file_hash VARCHAR(64) DEFAULT ''"))
        db.session.commit()

    if not inspector.has_table("saved_question"):
        db.create_all()


def _seed_qa_taxonomy():
    defaults = {
        "Identity Security Cloud": {
            "slug": "identity-security-cloud",
            "versions": ["Current", "2026.1", "2025.4"],
            "topics": ["Workflows", "Access Reviews", "Transforms", "Connectors", "APIs", "Provisioning"],
        },
        "IdentityIQ": {
            "slug": "identityiq",
            "versions": ["8.5", "8.4", "8.3"],
            "topics": ["Rules", "Lifecycle Events", "Certifications", "Connectors", "Provisioning"],
        },
        "Okta": {
            "slug": "okta",
            "versions": ["OIE", "Classic Engine"],
            "topics": ["Authentication", "Workflows", "Groups", "Applications", "APIs"],
        },
        "Other": {
            "slug": "other",
            "versions": ["General"],
            "topics": ["General", "Integration", "Troubleshooting"],
        },
    }
    for name, data in defaults.items():
        product = Product.query.filter_by(name=name).first()
        if product is None:
            product = Product(name=name, slug=data["slug"])
            db.session.add(product)
            db.session.flush()
        for label in data["versions"]:
            if ProductVersion.query.filter_by(product_id=product.id, label=label).first() is None:
                db.session.add(ProductVersion(product=product, label=label))
        for topic_name in data["topics"]:
            if Topic.query.filter_by(product_id=product.id, name=topic_name).first() is None:
                db.session.add(Topic(product=product, name=topic_name))
    db.session.commit()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from auth.auth import auth_bp
    from routes.admin.approvals import admin_approvals_bp
    from routes.admin.dashboard import admin_dashboard_bp
    from routes.admin.events import admin_events_bp
    from routes.admin.qa import admin_qa_bp
    from routes.admin.trends import admin_trends_bp
    from routes.admin.users import admin_users_bp
    from routes.api.api_routes import api_bp
    from routes.profile.activity import profile_activity_bp
    from routes.profile.edit_profile import edit_profile_bp
    from routes.profile.profile import profile_bp
    from routes.user.events import events_bp
    from routes.user.experts import experts_bp
    from routes.user.home import home_bp
    from routes.user.qa import qa_bp
    from routes.user.search import search_bp
    from routes.user.trends import trends_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(trends_bp)
    app.register_blueprint(qa_bp)
    app.register_blueprint(experts_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(edit_profile_bp)
    app.register_blueprint(profile_activity_bp)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_trends_bp)
    app.register_blueprint(admin_qa_bp)
    app.register_blueprint(admin_approvals_bp)
    app.register_blueprint(admin_events_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        _ensure_schema_updates(app)
        _seed_qa_taxonomy()
        sync_trend_sources(app)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True,port="5050" ,host="0.0.0.0")
