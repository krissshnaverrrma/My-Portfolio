import re
from flask import Blueprint, render_template, request, flash
from ..db.data import save_contact_message
from ..system.systems import limiter
contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/contact', methods=['GET', 'POST'])
@limiter.limit("5 per minute; 20 per day")
def contact():
    success = False
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        if not name or not email or not message:
            pass
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            pass
        else:
            is_saved = save_contact_message(name, email, subject, message)
            if is_saved:
                success = True
    return render_template('contact.html', success=success)
