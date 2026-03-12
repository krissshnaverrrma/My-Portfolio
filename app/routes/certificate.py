from flask import Blueprint, render_template, abort
from ..db.data import get_all_certifications, get_user_profile
certificate_bp = Blueprint('certificate', __name__)


@certificate_bp.route('/certificates')
def certificates():
    all_certs = get_all_certifications()
    user_profile = get_user_profile()
    return render_template(
        'certificate.html',
        certifications=all_certs,
        user_profile=user_profile
    )


@certificate_bp.route('/certificate/<slug>')
def certificate_detail(slug):
    certifications = get_all_certifications()
    cert = next((c for c in certifications if c.slug == slug), None)
    if not cert:
        abort(404)
    return render_template('certificate_detail.html', cert=cert)
