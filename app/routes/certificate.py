from flask import Blueprint, render_template, abort
from ..db.data import get_all_certifications
certificate_bp = Blueprint('certificate', __name__)


@certificate_bp.route('/certificate')
def certificate():
    certifications = get_all_certifications()
    return render_template('certificate.html', certifications=certifications)


@certificate_bp.route('/certificate/<slug>')
def certificate_detail(slug):
    certifications = get_all_certifications()
    cert = next((c for c in certifications if c.slug == slug), None)
    if not cert:
        abort(404)
    return render_template('certificate_detail.html', cert=cert)
