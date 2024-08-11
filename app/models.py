from email.policy import default
import uuid
from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(Admin_id):
    return Admin.query.get(Admin_id)


class Admin(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"Admin('{self.username}', '{self.email}')"
    


class Post(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    post_image = db.Column(db.String, nullable=False, default='def_post.png')
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String())
    author_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    images = db.relationship('Images', backref='post', lazy=True)



    def __repr__(self):
            return f"Post('{self.title}', '{self.content}')"

class Images(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String())
    filepath = db.Column(db.String())   
    post_id = db.Column(db.String, db.ForeignKey('post.id'), nullable=False)
