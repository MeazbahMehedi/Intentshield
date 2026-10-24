"""Application factory shared by the server, CLI and tests."""
from pathlib import Path
import os
import secrets
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from promptguard.database.db import init_db
from promptguard.security import install_security


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')
    app.config['DATABASE'] = app.config['DATABASE'] or str(Path(app.instance_path) / 'promptguard.sqlite3')
    if config:
        app.config.update(config)
    if not app.config.get('SECRET_KEY'):
        secret_path = Path(app.instance_path)/'session.key'
        secret_path.parent.mkdir(parents=True,exist_ok=True)
        try:
            fd=os.open(secret_path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            with os.fdopen(fd,'w') as key_file:key_file.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        app.config['SECRET_KEY']=secret_path.read_text().strip()
    init_db(app)
    from promptguard.services.github_profiles import GitHubProfiles
    app.extensions['github_profiles'] = GitHubProfiles(Path(app.config['DATABASE']).parent / 'github-public-profiles.json', app.config.get('GITHUB_TOKEN', ''))
    from promptguard.routes.main import main_bp
    from promptguard.routes.advanced import advanced_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(advanced_bp)
    install_security(app)
    @app.errorhandler(HTTPException)
    def error(exc):
        if request.path.startswith('/api/'):
            return jsonify(error=exc.description), exc.code
        return render_template('advanced_error.html', page_title='Request error', error=exc.description), exc.code
    return app
