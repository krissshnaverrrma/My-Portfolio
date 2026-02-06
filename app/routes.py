import os
import logging
from flask import Blueprint, jsonify, render_template, request, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import Config
from .data import (
    get_all_posts, get_all_projects, get_all_skills,
    get_timeline, get_services, get_user_profile
)
logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


@main_bp.context_processor
def inject_globals():
    """Injects global variables into all templates."""
    return {
        "is_ai_online": (hasattr(current_app, 'bot') and current_app.bot is not None),
        "contact_email": getattr(Config, 'CONTACT_EMAIL', os.getenv("CONTACT_EMAIL"))
    }


@main_bp.route('/')
def home():
    gh_profile = current_app.gh.get_profile() if hasattr(current_app, 'gh') else {}
    li_profile = current_app.li.get_profile() if hasattr(current_app, 'li') else {}
    return render_template('home.html', gh=gh_profile, li=li_profile)


@main_bp.route('/about')
def about():
    academic = get_timeline('academic')
    services = get_services()
    profile = get_user_profile()
    return render_template('about.html', academic=academic, services=services, profile=profile)


@main_bp.route('/projects')
def projects():
    projects_list = get_all_projects()
    return render_template('projects.html', projects=projects_list)


@main_bp.route('/blog')
def blog():
    posts = get_all_posts()
    return render_template('blog.html', posts=posts)


@main_bp.route('/blog/<slug>')
def blog_detail(slug):
    posts = get_all_posts()
    post = next((p for p in posts if p.slug == slug), None)
    profile = get_user_profile()
    if post:
        return render_template('blog_detail.html', post=post, profile=profile)
    return render_template('404.html'), 404


@main_bp.route('/skills')
def skills():
    all_skills = get_all_skills()
    journey = get_timeline('journey')
    profile = get_user_profile()
    return render_template('skills.html', skills=all_skills, journey=journey, profile=profile)


@main_bp.route('/resume')
def resume_page():
    return render_template('resume.html')


@main_bp.route('/contact')
def contact():
    profile = get_user_profile()
    return render_template('contact.html', profile=profile)


@main_bp.route('/certificate')
def certificate():
    name = request.args.get('name', 'Krishna Verma')
    return render_template('certificate.html', name=name)


@main_bp.route('/get_response', methods=['POST'])
def get_bot_response():
    if not hasattr(current_app, 'bot') or not current_app.bot:
        return jsonify({"response": "System is offline.", "status": "offline"})

    data = request.get_json()
    user_msg = data.get('message', '').strip()
    session_id = get_remote_address()

    if not user_msg:
        return jsonify({"response": "Empty message.", "status": "error"})

    try:
        reply, status = current_app.bot.get_response(
            user_msg, session_id=session_id)
        return jsonify({"response": reply, "status": status})
    except Exception as e:
        logger.error(f"❌ Chat Error: {e}")
        return jsonify({"response": "Error processing request.", "status": "error"}), 500
