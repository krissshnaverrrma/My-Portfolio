from flask import Blueprint, render_template
from ..db.data import get_timeline, get_services
about_bp = Blueprint('about', __name__)


@about_bp.route('/about')
def about():
    academic = get_timeline('academic')
    services = get_services()
    return render_template('about.html', academic=academic, services=services)
