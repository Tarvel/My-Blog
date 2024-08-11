from flask import Blueprint, url_for, request, redirect, render_template, flash
from app.models import Post

blog = Blueprint('blog', __name__, url_prefix='/blog',
               template_folder='templates')


@blog.route('/posts',methods=['POST', 'GET'])
@blog.route('/')
@blog.route('/posts/page/<int:page>',methods=['POST', 'GET'])
def posts(page=1):
    per_page = 5
    
    all_post = Post.query.filter_by(published=True)
    post = all_post.order_by(Post.updated_at.desc().nullslast(), Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('index.html', post=post)


@blog.route('/post/<string:slug>')
def actual_post(slug):
    post = Post.query.filter_by(slug=slug).first()
    return render_template('blog-post.html', post=post)

