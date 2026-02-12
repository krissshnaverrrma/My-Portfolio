from flask import Blueprint, render_template

resume_bp = Blueprint('resume', __name__)


@resume_bp.route('/resume')
def resume_page():
    return render_template('resume.html')


@resume_bp.route('/resume/print')
def resume_detail():
    return render_template('resume_detail.html')
