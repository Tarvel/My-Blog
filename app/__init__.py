import bleach
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DevelopmentConfig
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()



def create_app(config_class = DevelopmentConfig):
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    




    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    
    from app.models import Admin


    
    # Allowed tags and attributes
    allowed_tags = []
    allowed_attributes = {}

    def sanitize_and_truncate(content, length=120):
        # Sanitize the HTML content
        clean_content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, strip=True)
          # Replace &nbsp; with a space
        clean_content = clean_content.replace('&nbsp;', ' ')
        # Truncate the content
        if len(clean_content) > length:
            return clean_content[:length] + '...'
        return clean_content
    
    def format_date(value):
        return value.strftime('%Y-%m-%d')

    # Register the filter
    app.jinja_env.filters['sanitize_and_truncate'] = sanitize_and_truncate
    app.jinja_env.filters['format_date'] = format_date

    from app.blog import blog
    from app.admin import admin
    from app.main import route
    app.register_blueprint(admin.admin)
    app.register_blueprint(blog.blog)
    app.register_blueprint(route.main)


    return app
