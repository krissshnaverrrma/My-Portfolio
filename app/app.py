import logging
from flask import Flask
from .setup import configure_logging, setup_app

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)
    setup_app(app)
    return app
