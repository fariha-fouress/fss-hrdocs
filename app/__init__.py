"""Application factory."""
import os
from datetime import timedelta

from flask import Flask

from .config import Config
from .db import init_db


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.permanent_session_lifetime = timedelta(hours=12)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB uploads

    # ensure storage dirs exist (DB + uploaded letterheads live here)
    for d in (app.config.get("DATA_DIR"), app.config.get("UPLOAD_DIR")):
        if d:
            os.makedirs(d, exist_ok=True)

    init_db(app)

    # seed the built-in locations on first run so they become editable
    from .documents import registry as reg
    reg.seed_if_empty(app)

    from .auth import bp as auth_bp
    from .routes import bp as main_bp
    from .locations import bp as locations_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(locations_bp)

    @app.context_processor
    def inject_globals():
        return {"auth_mode": app.config["AUTH_MODE"]}

    # allow framing only by ourselves and Zoho (Recruit Web Tab)
    @app.after_request
    def set_frame_ancestors(response):
        response.headers["Content-Security-Policy"] = (
            "frame-ancestors 'self' https://*.zoho.com https://*.zoho.in"
        )
        return response

    return app
