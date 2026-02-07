from flask import Blueprint, render_template
from ..db.data import get_all_skills, get_timeline
skills_bp = Blueprint('skills', __name__)


@skills_bp.route('/skills')
def skills():
    all_skills = get_all_skills()
    journey = get_timeline('journey')
    return render_template('skills.html', skills=all_skills, journey=journey)
