from flask import Blueprint, render_template
from ..db.data import get_timeline, get_services, get_user_profile, get_interests, get_stats
about_bp = Blueprint('about', __name__)


@about_bp.route('/about')
def about():
    academic = get_timeline('academic')
    dev_journey = get_timeline('journey')
    services = get_services()
    interests = get_interests()
    user_profile = get_user_profile()
    stats = get_stats()
    return render_template(
        'about.html',
        academic_timeline=academic,
        dev_journey=dev_journey,
        services=services,
        interests=interests,
        user_profile=user_profile,
        stats=stats
    )
