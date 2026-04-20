from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24) # Required for session/flash messages

    # Register Main Blueprint
    from .routes import main
    app.register_blueprint(main)

    # Register Chatbot Blueprint
    # We import inside the function to avoid circular dependency issues
    from chatbot.app import chatbot
    app.register_blueprint(chatbot)

    return app