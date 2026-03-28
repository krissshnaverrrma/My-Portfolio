import uuid
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, flash, current_app, session, abort, jsonify
from ..essential import limiter
from ..db import (
    get_user_profile, get_timeline, get_services, get_interests, get_stats,
    load_json_data, get_all_projects, get_all_posts, get_all_certifications,
    save_contact_message, get_all_skills, get_core_principles,
    get_core_philosophy
)

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


def _get_item_or_404(items, slug):
    item = next((i for i in items if getattr(i, 'slug', None) == slug), None)
    return item or abort(404)


@main_bp.app_context_processor
def inject_globals():
    assistant = getattr(current_app, 'assistant', None)
    socials = getattr(current_app, 'socials', None)
    contact_email = current_app.config.get('CONTACT_EMAIL')
    if socials and getattr(socials, 'contact', None) and getattr(socials.contact, 'email', None):
        contact_email = socials.contact.email
    user_data = get_user_profile()
    return {
        "bot_status": assistant.status if assistant else "offline",
        "contact_email": contact_email,
        "socials": socials,
        "current_year": datetime.now().year,
        "profile": user_data,
        "user_profile": get_user_profile(),
        "stats": get_stats()
    }


@main_bp.route('/')
def home():
    return render_template('home.html')


@main_bp.route('/about')
def about():
    return render_template('about.html',
                           academic_timeline=get_timeline('academic'),
                           dev_journey=get_timeline('journey'),
                           services=get_services(),
                           interests=get_interests(),
                           stats=get_stats())


@main_bp.route('/skills')
def skills():
    return render_template('skills.html', skills=get_all_skills(),
                           core_principles=get_core_principles(),
                           core_philosophy=get_core_philosophy())


@main_bp.route('/resume')
def resume_page():
    return render_template('resume.html', **load_json_data())


@main_bp.route('/resume_print')
def resume_detail():
    return render_template('resume_detail.html', **load_json_data())


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html', success=False)
    name, email = request.form.get('name'), request.form.get('email')
    subject, message = request.form.get('subject'), request.form.get('message')
    if not (name and email and message):
        flash("Please Fill in Required Fields.", "warning")
        return render_template('contact.html', success=False)
    success = save_contact_message(name, email, subject, message)
    return render_template('contact.html', success=bool(success))


@main_bp.route('/projects')
def projects():
    return render_template('projects.html', projects=get_all_projects())


@main_bp.route('/project/<slug>')
def project_detail(slug):
    project = _get_item_or_404(get_all_projects(), slug)
    return render_template('project_detail.html', project=project)


@main_bp.route('/blogs')
def blogs():
    return render_template('blogs.html', posts=get_all_posts())


@main_bp.route('/blog/<slug>')
def blog_detail(slug):
    post = _get_item_or_404(get_all_posts(), slug)
    return render_template('blog_detail.html', post=post)


@main_bp.route('/certificates')
def certificates():
    return render_template('certificate.html', certifications=get_all_certifications())


@main_bp.route('/certificate/<slug>')
def certificate_detail(slug):
    cert = _get_item_or_404(get_all_certifications(), slug)
    return render_template('certificate_detail.html', cert=cert)


@main_bp.route('/assistant')
def assistant_page():
    session.setdefault('session_id', str(uuid.uuid4()))
    return render_template('assistant.html', title="AI Assistant")


@main_bp.route('/get_status', methods=['GET'])
def get_status():
    assistant = getattr(current_app, 'assistant', None)
    return jsonify({"status": assistant.status if assistant else "offline"})


@main_bp.route('/get_response', methods=['POST'])
@limiter.limit("15 per minute")
def get_response():
    user_input = request.json.get('message', '').strip()
    if not user_input:
        return jsonify({"response": "I didn't Catch that."}), 400
    if len(user_input) > 500:
        return jsonify({"response": "Your Message is too Long. Please Keep it under 500 Characters."}), 400
    try:
        service = getattr(current_app, 'assistant',
                          getattr(current_app, 'bot', None))
        if not service:
            raise Exception("AI Assistant Service not Initialized")
        session_id = session.get('session_id', str(uuid.uuid4()))
        result = service.get_response(user_input, session_id=session_id)
        return jsonify({
            "response": result.get('reply'),
            "status": result.get('status')
        })
    except Exception as e:
        logger.error(f"❌ Chat Route Error: {e}")
        return jsonify({"response": "System is Temporarily Unavailable.", "status": "offline"}), 500
