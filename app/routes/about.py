from flask import Blueprint, render_template
from ..db.data import get_timeline, get_services, get_user_profile
about_bp = Blueprint('about', __name__)


@about_bp.route('/about')
def about():
    academic = get_timeline('academic')
    services = get_services()
    user_profile = get_user_profile()
    return render_template(
        'about.html',
        academic_timeline=academic,
        services=services,
        user_profile=user_profile
    )
