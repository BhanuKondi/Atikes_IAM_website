from flask import Flask
from pathlib import Path

from .config import Config
from .extensions import db, login_manager
from .models import User


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

    from .routes.auth import auth_bp
    from .routes.experts import experts_bp
    from .routes.main import main_bp
    from .routes.qa import qa_bp
    from .routes.trends import trends_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(trends_bp)
    app.register_blueprint(qa_bp)
    app.register_blueprint(experts_bp)

    with app.app_context():
        db.create_all()

    return app
