"""PromptGuard Flask application factory."""
from flask import Flask
from promptguard.routes.main import main_bp

def create_app():
    app = Flask(__name__, instance_relative_config=True,
                template_folder="templates", static_folder="static")
    app.config.from_object("config.Config")
    app.register_blueprint(main_bp)
    return app
