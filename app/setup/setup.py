import logging
import flask.cli
from flask import Flask
from ..essential import markdown_filter, format_date, limiter

logger = logging.getLogger(__name__)


def configure_logging():
    from ..config import Config
    if Config.IS_RENDER:
        logging.disable(logging.CRITICAL)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s'
        )
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        logging.getLogger("flask").setLevel(logging.ERROR)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("google.genai").setLevel(logging.WARNING)
        flask.cli.show_server_banner = lambda *args: None


def setup_app(app: Flask):
    from ..config import get_config
    from ..db import init_db_session
    from ..routes import register_routes
    from ..service import initialize_app_services
    app.config.from_object(get_config())
    limiter.init_app(app)
    register_routes(app)
    app.jinja_env.filters['markdown'] = markdown_filter
    app.jinja_env.filters['format_date'] = format_date
    initialize_app_services(app)
    init_db_session(app)
