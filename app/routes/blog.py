from flask import Blueprint, render_template, abort
from ..db.data import get_all_posts, get_user_profile
blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/blogs')
def blogs():
    posts = get_all_posts()
    user_profile = get_user_profile()
    return render_template('blogs.html', posts=posts, user_profile=user_profile)


@blog_bp.route('/blog/<slug>')
def blog_detail(slug):
    posts = get_all_posts()
    post = next((p for p in posts if p.slug == slug), None)
    if post:
        return render_template('blog_detail.html', post=post)
    abort(404)
