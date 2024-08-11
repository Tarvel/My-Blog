from app import create_app
import create_admin, secrets, os

app = create_app()


@app.before_request
def initialize():
        create_admin()


