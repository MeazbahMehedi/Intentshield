"""Shared pytest setup."""

import pytest

from promptguard import create_app


@pytest.fixture
def client():
    """A Flask test client. It calls routes without opening a browser."""
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client
