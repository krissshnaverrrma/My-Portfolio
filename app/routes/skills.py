from flask import Blueprint, render_template
from ..db.data import get_all_skills, get_skill_by_slug, get_core_principles, get_core_philosophy
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


@skills_bp.route('/skill/<slug>')
def skill_detail(slug):
    skill = get_skill_by_slug(slug)
    if not skill:
        abort(404)
    return render_template('skill_detail.html', skill=skill)
