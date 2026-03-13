from flask import Blueprint, render_template
from ..db.data import get_user_profile
home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    user_profile = get_user_profile()
    return render_template('home.html', profile=user_profile)
