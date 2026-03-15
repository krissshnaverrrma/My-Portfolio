import os
import json
import uuid
import logging
import re
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, abort, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from ..db.data import (
    get_user_profile, get_timeline, get_services, get_interests, get_stats,
    _get_project_root_path, load_json_data, seed_initial_data,
    get_all_posts, get_all_certifications, save_contact_message,
    get_all_projects, get_all_skills, get_core_principles, get_core_philosophy
)
import app.db.data as db_data
from ..system.systems import limiter
from ..assistant.assistant_response import log_assistant_response
logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@main_bp.app_context_processor
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


@main_bp.route('/')
def home():
    user_profile = get_user_profile()
    return render_template('home.html', profile=user_profile)


@main_bp.route('/about')
def about():
    return render_template(
        'about.html',
        academic_timeline=get_timeline('academic'),
        dev_journey=get_timeline('journey'),
        services=get_services(),
        interests=get_interests(),
        user_profile=get_user_profile(),
        stats=get_stats()
    )


@main_bp.route('/skills')
def skills():
    user_profile = get_user_profile()
    return render_template(
        'skills.html',
        skills=get_all_skills(),
        skills_description=user_profile.get('skills_description', ''),
        core_principles=get_core_principles(),
        core_philosophy=get_core_philosophy()
    )


def load_portfolio_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, 'db', 'data.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@main_bp.route('/resume')
def resume_page():
    data = load_portfolio_data()
    return render_template('resume.html', **data)


@main_bp.route('/resume_print')
def resume_detail():
    data = load_portfolio_data()
    return render_template('resume_detail.html', **data)


@main_bp.route('/contact', methods=['GET', 'POST'])
@limiter.limit("5 per minute; 20 per day")
def contact():
    success = False
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        if not name or not email or not message:
            pass
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            pass
        else:
            is_saved = save_contact_message(name, email, subject, message)
            if is_saved:
                success = True
    user_profile = get_user_profile()
    return render_template('contact.html', success=success)


@main_bp.route('/projects')
def projects():
    all_projects = get_all_projects()
    user_profile = get_user_profile()
    return render_template('projects.html', projects=all_projects, user_profile=user_profile)


@main_bp.route('/project/<slug>')
def project_detail(slug):
    projects_list = get_all_projects()
    project = next((p for p in projects_list if p.slug == slug), None)
    if project:
        return render_template('project_detail.html', project=project)
    abort(404)


@main_bp.route('/blogs')
def blogs():
    posts = get_all_posts()
    user_profile = get_user_profile()
    return render_template('blogs.html', posts=posts, user_profile=user_profile)


@main_bp.route('/blog/<slug>')
def blog_detail(slug):
    posts = get_all_posts()
    post = next((p for p in posts if p.slug == slug), None)
    if post:
        return render_template('blog_detail.html', post=post)
    abort(404)


@main_bp.route('/certificates')
def certificates():
    all_certs = get_all_certifications()
    user_profile = get_user_profile()
    return render_template('certificate.html', certifications=all_certs, user_profile=user_profile)


@main_bp.route('/certificate/<slug>')
def certificate_detail(slug):
    certifications = get_all_certifications()
    cert = next((c for c in certifications if c.slug == slug), None)
    if not cert:
        abort(404)
    return render_template('certificate_detail.html', cert=cert)


@main_bp.route('/assistant')
def assistant_page():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('assistant.html', title="AI Assistant")


@main_bp.route('/get_status', methods=['GET'])
def get_status():
    if hasattr(current_app, 'assistant') and current_app.assistant:
        if current_app.assistant.is_online:
            return jsonify({"status": "online"})
        else:
            return jsonify({"status": "database"})
    return jsonify({"status": "offline"})


@main_bp.route('/get_response', methods=['POST'])
@limiter.limit("15 per minute")
def get_response():
    user_input = request.json.get('message')
    if not user_input or len(user_input.strip()) == 0:
        return jsonify({"response": "I didn't catch that."}), 400
    if len(user_input) > 500:
        return jsonify({"response": "Your Message is too Long. Please Keep it under 500 Characters."}), 400
    session_id = session.get('session_id', str(uuid.uuid4()))
    try:
        service = getattr(current_app, 'assistant',
                          getattr(current_app, 'bot', None))
        if not service:
            raise Exception("AI Assistant Service not Initialized")
        response, status = service.get_response(
            user_input, session_id=session_id)
        return jsonify({
            "response": response,
            "status": status
        })
    except Exception as e:
        logger.error(f"❌ Chat Route Error: {e}")
        return jsonify({"response": "System is Temporarily Unavailable."}), 500


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def resize_image(image_path, target_width=300):
    img = Image.open(image_path)
    width_percent = (target_width / float(img.size[0]))
    height_size = int((float(img.size[1]) * float(width_percent)))
    img = img.resize((target_width, height_size), Image.Resampling.LANCZOS)
    img.save(image_path)


@admin_bp.route('/', methods=['GET', 'POST'])
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'is_admin' in session:
        return redirect(url_for('admin.panel'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        expected_username = current_app.config.get('ADMIN_USERNAME')
        expected_password = current_app.config.get('ADMIN_PASSWORD')
        if expected_username and expected_password and username == expected_username and password == expected_password:
            session.permanent = True
            session['is_admin'] = True
            return redirect(url_for('admin.panel'))
        else:
            flash('Invalid Username or Password.', 'danger')
    return render_template('admin_login.html')


@admin_bp.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'is_admin' not in session:
        return redirect(url_for('admin.login'))
    json_path = _get_project_root_path('app/db/data.json')
    data = load_json_data()
    if request.method == 'POST':
        section = request.form.get('section')
        if section == 'profile':
            data['user_profile']['name'] = request.form.get('name')
            data['user_profile']['contact_email'] = request.form.get(
                'contact_email')
            data['user_profile']['contact_phone'] = request.form.get(
                'contact_phone')
            data['user_profile']['location'] = request.form.get('location')
            data['user_profile']['philosophy'] = request.form.get('philosophy')
            data['user_profile']['focus'] = request.form.get('focus')
            data['user_profile']['about_text'] = request.form.get('about_text')
            if 'profile_photo' in request.files:
                file = request.files['profile_photo']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    upload_path = os.path.join(
                        current_app.root_path, 'static', 'assets', 'profile', 'profile.jpg')
                    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                    file.save(upload_path)
                    resize_image(upload_path)
                    data['user_profile']['profile_image'] = '/static/assets/profile/profile.jpg'
                    flash('Profile and Photo Updated!', 'success')
                elif file and file.filename != '':
                    flash('Invalid file type.', 'warning')
            else:
                flash('Profile Updated!', 'success')
        elif section in ['projects', 'skills', 'blog_posts', 'certifications']:
            idx = int(request.form.get('item_index'))
            if section == 'projects':
                data['projects'][idx].update({
                    'title': request.form.get('title'),
                    'description': request.form.get('description'),
                    'demo_url': request.form.get('demo_url'),
                    'github_url': request.form.get('github_url')
                })
            elif section == 'skills':
                data['skills'][idx].update({
                    'name': request.form.get('name'),
                    'description': request.form.get('description'),
                    'icon': request.form.get('icon')
                })
            elif section == 'blog_posts':
                data['blog_posts'][idx].update({
                    'title': request.form.get('title'),
                    'summary': request.form.get('summary')
                })
            elif section == 'certifications':
                data['certifications'][idx].update({
                    'title': request.form.get('title'),
                    'issuer': request.form.get('issuer'),
                    'status': request.form.get('status')
                })
            flash(f'{section.replace("_", " ").capitalize()} Updated!', 'success')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        db_data._JSON_CACHE = None
        seed_initial_data(f"Admin Update: {section}")
        return redirect(url_for('admin.panel'))
    return render_template('admin.html', data=data)


@admin_bp.route('/logout')
def logout():
    session.pop('is_admin', None)
    return render_template('admin_logout.html')
