import logging
import traceback
from flask import Flask
from .config import Config
from .routes import main_bp, limiter

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    limiter.init_app(app)
    with app.app_context():
        from .data import init_db, GitHubPortfolio, LinkedInPortfolio
        from .chat_bot import init_bot
        print("🚀 Initializing the System and Modules")
        try:
            logger.info("🔹 Services: Waking up AI and Fetching Services...")
            logger.info(
                f"✅ AI Initialized and Connected to Tier: {Config.GEMINI_MODEL if Config.GEMINI_MODEL else 'Auto-Selection'}"
            )
            init_db()
            app.bot = init_bot()
            app.gh = GitHubPortfolio()
            app.li = LinkedInPortfolio()
            logger.info(
                "✅ All the Configuration and Services Initialized Successfully")
        except Exception as e:
            logger.warning(f"❌ Service Initialization Warning: {e}")
            traceback.print_exc()
            app.bot, app.gh, app.li = None, None, None
    app.register_blueprint(main_bp)
    return app


app = create_app()
