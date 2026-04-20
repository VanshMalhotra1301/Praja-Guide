from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'praja-guide-default-dev-key-change-in-prod')

    # Register Main Blueprint
    from .routes import main
    app.register_blueprint(main)

    return app