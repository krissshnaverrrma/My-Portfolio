from flask import Blueprint, render_template
from ..db.data import get_all_projects
projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects')
def projects():
    projects_list = get_all_projects()
    return render_template('projects.html', projects=projects_list)
