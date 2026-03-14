from flask import Blueprint, render_template
from ..db.data import get_all_skills, get_core_principles, get_core_philosophy
skills_bp = Blueprint('skills', __name__)


@skills_bp.route('/skills')
def skills():
    skills_data = get_all_skills()
    core_principles = get_core_principles()
    core_philosophy = get_core_philosophy()
    return render_template(
        'skills.html',
        skills=skills_data,
        core_principles=core_principles,
        core_philosophy=core_philosophy
    )
