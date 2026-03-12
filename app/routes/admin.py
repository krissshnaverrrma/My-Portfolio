import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from werkzeug.utils import secure_filename
from ..db.data import _get_project_root_path, load_json_data, seed_initial_data
import app.db.data as db_data
from PIL import Image

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
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
