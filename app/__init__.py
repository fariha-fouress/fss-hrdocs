"""Application factory."""
from datetime import timedelta

from flask import Flask

from .config import Config
from .db import init_db


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.permanent_session_lifetime = timedelta(hours=12)

    init_db(app)

    from .auth import bp as auth_bp
    from .routes import bp as main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_globals():
        return {"auth_mode": app.config["AUTH_MODE"]}

    return app
