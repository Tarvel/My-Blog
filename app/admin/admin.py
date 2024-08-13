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


@admin.route('/dashboard', methods=['GET', 'POST'])
@admin.route('/dashboard/page/<int:page>', methods=['GET', 'POST'])
@login_required
def dashboard(page=1):
    per_page = 4

    post = Post.query.filter().order_by(Post.updated_at.desc().nullslast(), Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # post = all_post.order_by(Post.updated_at.desc().nullslast(), Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    if request.method == 'POST':
        filter_value = request.form.get('filterValue')
        if filter_value == 'All':
            all_post = Post.query.filter()
            post = all_post.order_by(Post.updated_at.desc().nullslast(), Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
            return render_template('dashboard.html', post=post, title='Dashboard')
        elif filter_value == 'Draft':
            all_post = Post.query.filter_by(published=False)
            post = all_post.order_by(Post.updated_at.desc().nullslast(), Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
            return render_template('dashboard.html', post=post, title='Dashboard')
        elif filter_value == 'Published':
            all_post = Post.query.filter_by(published=True)
            post = all_post.order_by(Post.updated_at.desc().nullslast(), Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
            return render_template('dashboard.html', post=post, title='Dashboard')
        else:
            # Default logic or error handling
            pass            
        
    return render_template('dashboard.html', post=post, title='Dashboard')
    



@admin.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('blog.posts'))



@admin.route('/create_post', methods=['POST', 'GET'])
def create_post():
    if current_user.is_authenticated:
        form = PostForm()

        if request.method == 'POST':
            action = request.form.get('action')  # Get the action value from the form
            title = form.title.data
            content = form.content.data
            tags = form.tags.data
            author_id = current_user.id

            # Slug generation logic
            base_slug = slugify(title)
            slug = base_slug
            count = 1
            while Post.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{count}"
                count += 1

            # Handle the form submission based on action
            published = (action != 'draft')  # Published if action is not 'draft'
            
            # Create a new post
            post = Post(
                title=title.title(),
                content=content,
                tags=tags,
                published=published,
                author_id=author_id,
                slug=slug
            )

            # Handle file upload
            if form.post_image.data:
                img_file = save_pic(form.post_image.data)
                post.post_image = img_file
            
            # Add and commit the post to the database
            db.session.add(post)
            db.session.commit()
            
            # Flash a message based on action
            if action == 'draft':
                flash('Saved to Drafts')
            elif action == 'publish':
                flash('Post Published')
            
            # Redirect to dashboard
            return redirect(url_for('admin.dashboard'))
        
        elif request.method == 'GET':
            # If it's a GET request, just render the form
            return render_template('create_post.html', form=form, title='Create Post')

    else:
        return redirect(url_for('blog.post'))



    
@admin.route('/upload_image', methods=['POST'])
@login_required
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




@admin.route('/edit_post/<string:slug>', methods=['POST', 'GET'])
@login_required
def edit_post(slug):
    if current_user.is_authenticated:
        form = PostForm()
        post = Post.query.filter_by(slug=slug).first()

        if request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
            form.tags.data = post.tags
        
        if request.method == 'POST':
            action = request.form.get('action')  # Get the action value from the form
            post.title = form.title.data
            post.content = form.content.data
            post.tags = form.tags.data
            post.author_id = current_user.id

            published = (action != 'draft')

            # Slug generation logic
            base_slug = slugify(form.title.data)
            slug = base_slug
            count = 1
            while Post.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{count}"
                count += 1

            if form.post_image.data:
                img_file = save_pic(form.post_image.data)
                post.post_image = img_file
                
            post.published = published

            db.session.add(post)
            db.session.commit()

            if action == 'draft':
                flash('Saved to Drafts')
            elif action == 'publish':
                flash('Post Edited')
            
            # Redirect to dashboard
            return redirect(url_for('admin.dashboard'))

            
    return render_template('edit_post.html', form=form, title='Edit Post')
