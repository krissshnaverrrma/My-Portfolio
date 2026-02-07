from flask import Blueprint, render_template, current_app
home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    gh_profile = current_app.gh.get_profile() if hasattr(current_app, 'gh') else {}
    li_profile = current_app.li.get_profile() if hasattr(current_app, 'li') else {}
    return render_template('home.html', gh=gh_profile, li=li_profile)
