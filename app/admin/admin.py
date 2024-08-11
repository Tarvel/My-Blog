import os, secrets, uuid
from slugify import slugify
from flask import Blueprint, url_for, request, redirect, render_template, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Admin, Post, Images
from app.wtforms import LoginForm, PostForm
from app import db


admin = Blueprint('admin', __name__, url_prefix='/admin',
                  template_folder='templates',
                  static_folder='static')

def save_pic(form_img):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_img.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/post_image', picture_fn)
    form_img.save(picture_path)
    return picture_fn

@admin.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    else:
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data

            user = Admin.query.filter_by(email=email).first()

            if user and user.password == password:
                login_user(user)
                flash('Login successful, Welcome ' + user.username)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
            else:
                flash('If you are the admin of this blog you should know your own login details')
                return redirect(url_for('admin.login'))

        return render_template('login.html', form=form)

@admin.route('/dashboard')
@login_required
def dashboard():
    return "DASHBOARD"



@admin.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('blog.posts'))



@admin.route('/create_post', methods=['POST', 'GET'])
def create_post():
    if current_user.is_authenticated:
        form = PostForm()
        action = request.form.get('action')

        
        title = form.title.data
        content = form.content.data
        tags = form.tags.data
        published = True if action != 'draft' else False
        author_id = current_user.id

        if title:
            base_slug = slugify(title)
            slug = base_slug
            count = 0
            slug_check = Post.query.filter_by(slug=slug).first()
            if slug_check is None:
                pass
            else:
                while count <= len(slug_check):
                    new_slug = slug + count
                    count += 1
                    slug = str(new_slug)
            
        else:
            pass

        if form.validate_on_submit():  
            post = Post(
                    title=title.title(),
                    content=content,
                    tags=tags,
                    published=published,
                    author_id=author_id,
                    slug=slug
                )
                
            if form.post_image.data:
                img_file = save_pic(form.post_image.data)
                post.post_image = img_file
            
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('admin.dashboard'))


        if action == 'draft':
            post = Post(
                    title=title.title(),
                    content=content,
                    tags=tags,
                    author_id=author_id,
                    slug=slug
                )
                
            if form.post_image.data:
                img_file = save_pic(form.post_image.data)
                post.post_image = img_file
            flash('Saved to Drafts')
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('admin.dashboard'))

            
        elif action == 'cancel':
            return redirect(url_for('admin.dashboard'))

        return render_template('create_post.html', form=form)
    else:
        return redirect(url_for('blog.post'))

@admin.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file:
        unique_filename = str(uuid.uuid4()) + "_" + file.filename
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        new_image = Images(filename=unique_filename, filepath=filepath)
        db.session.add(new_image)
        db.session.commit()
        
        return {'location': url_for('static', filename='post_image/' + unique_filename)}
