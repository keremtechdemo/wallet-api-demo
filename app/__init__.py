from flask import Flask

from . import config
from .db import init_db
from .routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.JWT_SECRET
    init_db()
    app.register_blueprint(api)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
