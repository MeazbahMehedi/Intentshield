"""Isolated application database for every test."""
import pytest
from promptguard import create_app

@pytest.fixture
def app(tmp_path):
    return create_app({'TESTING':True,'DATABASE':str(tmp_path/'test.sqlite3'),'SECRET_KEY':'test-key','RATE_LIMIT':1000})

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
