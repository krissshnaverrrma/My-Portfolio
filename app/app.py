import os
import logging
import traceback
from flask import Flask
from .config.config import Config
from .db.data import init_db, get_user_profile
from .routes import register_routes
from .errors import errors_bp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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

        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
            try:
                if app.debug:
                    print("🚀 Initializing the Systems and Modules")
                    logger.info(
                        "🔹 Services: Fetching and Initializing All Components")

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
                    print("All Systems and Modules Initialized Successfully! 🚀")

                print(
                    f"Running in {'Production' if not app.debug else 'Development'} Mode 🚀")

            except Exception as e:
                if app.debug:
                    logger.warning(f"❌ Service Initialization Warning: {e}")
                    traceback.print_exc()

                app.assistant, app.gh, app.li = None, None, None

    @app.context_processor
    def inject_global_context():
        return {"profile": get_user_profile()}

    return app
