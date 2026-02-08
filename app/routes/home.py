from flask import Blueprint, render_template, current_app
home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    gh_service = getattr(current_app, 'gh', None)
    li_service = getattr(current_app, 'li', None)
    gh_profile = gh_service.get_profile() if gh_service else {}
    li_profile = li_service.get_profile() if li_service else {}

    return render_template('home.html', gh=gh_profile, li=li_profile)
