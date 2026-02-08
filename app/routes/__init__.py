import os
from datetime import datetime
from flask import Blueprint, current_app
from ..config.config import Config
hub_bp = Blueprint('hub', __name__)


@hub_bp.app_context_processor
def inject_globals():
    """Provides common variables and system status to all templates."""
    bot_status = "offline"
    if hasattr(current_app, 'assistant') and current_app.assistant is not None:
        bot_status = "online" if getattr(
            current_app.assistant, 'is_online', False) else "database"
    return {
        "bot_status": bot_status,
        "contact_email": getattr(Config, 'CONTACT_EMAIL', os.getenv("CONTACT_EMAIL")),
        "current_year": datetime.now().year
    }


def register_routes(app):
    """
    Imports and registers all individual route blueprints with the Flask app.
    """
    from .home import home_bp
    from .about import about_bp
    from .skills import skills_bp
    from .resume import resume_bp
    from .contact import contact_bp
    from .blog import blog_bp
    from .projects import projects_bp
    from .certificate import certificate_bp
    from .assistant import assistant_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(certificate_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(hub_bp)
