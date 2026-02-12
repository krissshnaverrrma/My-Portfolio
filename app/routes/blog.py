from flask import Blueprint, render_template, abort
from ..db.data import get_all_posts
blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/blog')
def blog_list():
    posts = get_all_posts()
    return render_template('blog.html', posts=posts)


@blog_bp.route('/blog/<slug>')
def blog_detail(slug):
    posts = get_all_posts()
    post = next((p for p in posts if p.slug == slug), None)
    if post:
        return render_template('blog_detail.html', post=post)
    abort(404)
