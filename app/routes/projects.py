from flask import Blueprint, render_template, abort
from ..db.data import get_all_projects, get_user_profile
projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects')
def projects():
    all_projects = get_all_projects()
    user_profile = get_user_profile()
    return render_template(
        'projects.html',
        projects=all_projects,
        user_profile=user_profile
    )


@projects_bp.route('/projects/<slug>')
def project_detail(slug):
    projects_list = get_all_projects()
    project = next((p for p in projects_list if p.slug == slug), None)
    if project:
        return render_template('project_detail.html', project=project)
    abort(404)
