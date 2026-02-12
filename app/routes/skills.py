from flask import Blueprint, render_template, abort
from ..db.data import get_all_skills, get_timeline, get_skill_by_slug

skills_bp = Blueprint('skills', __name__)


@skills_bp.route('/skills')
def skills():
    all_skills = get_all_skills()
    journey = get_timeline('journey')
    return render_template('skills.html', skills=all_skills, journey=journey)


@skills_bp.route('/skill/<slug>')
def skill_detail(slug):
    skill = get_skill_by_slug(slug)
    if not skill:
        abort(404)
    return render_template('skill_detail.html', skill=skill)
