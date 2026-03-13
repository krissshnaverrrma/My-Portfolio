import os
import logging
import flask.cli
from flask import Flask
from flasgger import Swagger
from .config.config import get_config
from .db.data import get_user_profile
from .db.database import db_session
from .routes import register_routes
from .system.systems import limiter, format_date, markdown_filter, configure_logging, initialize_app_services
flask.cli.show_server_banner = lambda *args: None
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    is_cli_mode, is_quiet_mode = configure_logging()
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)
    app = Flask(__name__)
    app.config.from_object(get_config())
    limiter.init_app(app)
    Swagger(app)
    register_routes(app)
    app.jinja_env.filters['markdown'] = markdown_filter
    app.jinja_env.filters['format_date'] = format_date
    initialize_app_services(app, is_cli_mode, is_quiet_mode)

    @app.context_processor
    def inject_global_context() -> dict:
        return {"profile": get_user_profile()}

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app
