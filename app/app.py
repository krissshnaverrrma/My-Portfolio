import os
import logging
import traceback
from flask import Flask
from .config.config import Config
from .db.data import init_db, get_user_profile
from .routes import register_routes
from .errors import errors_bp
from flask_limiter import Limiter
from .runtime.runtime import PortfolioRuntime
from .diagnostics import DiagnosticEngine
from .extensions import limiter
from .utils.filters import markdown_filter
from .utils.helpers import format_date
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    limiter.init_app(app)
    register_routes(app)
    app.register_blueprint(errors_bp)
    app.jinja_env.filters['markdown'] = markdown_filter
    app.jinja_env.filters['format_date'] = format_date
    with app.app_context():
        from .social.socials import init_github, init_linkedin
        from .assistant.assistant import init_assistant
        is_testing = os.environ.get("FLASK_TESTING") == "true"
        if (os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug) and not is_testing:
            try:
                if app.debug:
                    print("Initializing All the Systems")
                    print(
                        "Fetching All the Components")
                init_db()
                app.assistant = init_assistant()
                app.gh = init_github()
                app.li = init_linkedin()
                if app.assistant:
                    runtime = PortfolioRuntime(app.assistant)
                    runtime.verify_identity()
                    diag = DiagnosticEngine(app)
                    diag.run_route_audit()
                if app.debug:
                    print("All the Systems Initialized Successfully!")
            except Exception as e:
                if app.debug:
                    logger.warning(f"Initialization Warning: {e}")
                    traceback.print_exc()
                app.assistant, app.gh, app.li = None, None, None

    @app.context_processor
    def inject_global_context():
        return {"profile": get_user_profile()}
    return app
