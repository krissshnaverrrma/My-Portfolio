from flask import Blueprint, render_template, request
from ..db.data import save_contact_message
contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    success = False
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        if name and email and message:
            save_contact_message(name, email, subject, message)
            success = True
    return render_template('contact.html', success=success)
