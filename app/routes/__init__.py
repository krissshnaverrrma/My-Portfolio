import os
from datetime import datetime
from flask import Blueprint, current_app
from .admin import admin_bp
hub_bp = Blueprint('hub', __name__)


@hub_bp.app_context_processor
def inject_globals():
    assistant = getattr(current_app, 'assistant', None)
    bot_status = "offline"
    if assistant:
        bot_status = "online" if getattr(
            assistant, 'is_online', False) else "database"
    return {
        "bot_status": bot_status,
        "contact_email": current_app.config.get('CONTACT_EMAIL'),
        "current_year": datetime.now().year
    }


def register_routes(app):
    from .home import home_bp
    from .about import about_bp
    from .skills import skills_bp
    from .resume import resume_bp
    from .contact import contact_bp
    from .blog import blog_bp
    from .projects import projects_bp
    from .certificate import certificate_bp
    from .assistant import assistant_bp
    blueprints = [
        home_bp, about_bp, skills_bp, resume_bp, contact_bp,
        blog_bp, projects_bp, certificate_bp, assistant_bp, hub_bp, admin_bp
    ]
    for bp in blueprints:
        app.register_blueprint(bp)
