from flask import Blueprint, render_template, request
from ..db.data import get_all_certifications
certificate_bp = Blueprint('certificate', __name__)


@certificate_bp.route('/certificate')
def certificate():
    name = request.args.get('name', 'Krishna Verma')
    certifications = get_all_certifications()
    return render_template('certificate.html', name=name, certifications=certifications)
