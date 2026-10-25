"""SQLite persistence; all records are scoped to a workspace identity."""
import json
import sqlite3
import time
from pathlib import Path
from flask import current_app, g, session
from uuid import uuid4

SCHEMA = Path(__file__).with_name('schema.sql').read_text(encoding='utf-8')


def db():
    if 'db' not in g:
        path = current_app.config['DATABASE']
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(path, timeout=15)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db(app):
    with app.app_context():
        db().executescript(SCHEMA)
        db().commit()
    @app.teardown_appcontext
    def close_db(error=None):
        connection = g.pop('db', None)
        if connection:
            connection.close()


def owner():
    if getattr(g, 'service', False):
        return 'service'
    if session.get('user'):
        return 'user:' + session['user']
    if 'workspace' not in session:
        session['workspace'] = uuid4().hex
    return session['workspace']


def settings():
    row = db().execute('SELECT data FROM settings WHERE owner=?', (owner(),)).fetchone()
    return json.loads(row['data']) if row else {}


def save_settings(data):
    db().execute('INSERT OR REPLACE INTO settings VALUES (?,?)', (owner(), json.dumps(data)))
    db().commit()


def audit(event, data):
    db().execute('INSERT INTO audit(owner,stamp,event,data) VALUES (?,?,?,?)', (owner(), time.time(), event, json.dumps(data)))
    db().commit()


def prune():
    cutoff = time.time() - settings().get('retention_days', 30) * 86400
    for table in ('scans', 'experiments', 'audit'):
        db().execute(f'DELETE FROM {table} WHERE owner=? AND stamp<?', (owner(), cutoff))
    db().commit()


def history():
    prune()
    rows = db().execute('SELECT data FROM scans WHERE owner=? ORDER BY stamp DESC LIMIT 2000', (owner(),)).fetchall()
    return [json.loads(x['data']) for x in rows]
