from flask import redirect, url_for, Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('blog.posts'))