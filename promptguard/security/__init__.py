"""Request validation, optional authentication, roles, CSRF and persistent quotas."""
import hmac
import secrets
import time
from functools import wraps
from urllib.parse import urlparse
from flask import abort, current_app, g, jsonify, redirect, request, session, url_for
from promptguard.database.db import db, owner


def csrf_token():
    if 'csrf' not in session:
        session['csrf'] = secrets.token_hex(24)
    return session['csrf']


def admin_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if current_app.config['AUTH_REQUIRED'] and session.get('role') != 'admin':
            abort(403, description='Administrator role required.')
        return func(*args, **kwargs)
    return wrapped


def install_security(app):
    app.jinja_env.globals['csrf_token'] = csrf_token
    @app.before_request
    def protect():
        token = current_app.config.get('API_TOKEN')
        auth = request.headers.get('Authorization', '')
        g.service = bool(token and auth.startswith('Bearer ') and hmac.compare_digest(auth[7:], token))
        public = request.endpoint in ('advanced.login', 'main.health', 'static')
        service_endpoints = {'main.api_scan', 'main.api_batch', 'advanced.document_scan', 'advanced.gateway'}
        if g.service and request.endpoint not in service_endpoints:
            g.service = False
        if app.config['AUTH_REQUIRED'] and not public and not session.get('user') and not g.service:
            if request.path.startswith('/api/'):
                return jsonify(error='Authentication required.'), 401
            return redirect(url_for('advanced.login'))
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            origin = request.headers.get('Origin')
            if origin and urlparse(origin).netloc != request.host:
                abort(403, description='Cross-origin writes are disabled.')
            supplied = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token', '')
            if not app.config['TESTING'] and not g.service and not hmac.compare_digest(supplied, csrf_token()):
                abort(403, description='Missing or invalid CSRF token. Reload the page.')
            bucket = ('login:' + (request.remote_addr or 'local')) if request.endpoint == 'advanced.login' else owner()
            now = time.time()
            connection = db()
            connection.execute('BEGIN IMMEDIATE')
            row = connection.execute('SELECT window,hits FROM limits WHERE bucket=?', (bucket,)).fetchone()
            hits = row['hits'] + 1 if row and now-row['window'] < 60 else 1
            window = row['window'] if row and now-row['window'] < 60 else now
            connection.execute('INSERT OR REPLACE INTO limits VALUES (?,?,?)', (bucket, window, hits))
            connection.execute('DELETE FROM limits WHERE window<?', (now-120,))
            connection.commit()
            if hits > app.config['RATE_LIMIT']:
                return jsonify(error='Rate limit exceeded. Retry in one minute.'), 429, {'Retry-After': '60'}

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        return response
