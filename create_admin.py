def create_admin():
    
    from app import db, create_app
    app = create_app()

    with app.app_context():

        import os
        from app.models import Admin
        from dotenv import load_dotenv

        load_dotenv()
        
        username = os.getenv('ADMIN_USERNAME')
        email=os.getenv('ADMIN_EMAIL')
        password = os.getenv('ADMIN_PASSWORD')
        
        if username in Admin.query.all():
            pass
        else:
            admin_detail = Admin( username = username, 
                            email=email,
                            password=password)
            db.session.add(admin_detail)
            db.session.commit()
            