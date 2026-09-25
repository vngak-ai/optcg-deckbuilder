import pytest

from app.factory import create_app


@pytest.fixture
def app():
    return create_app(seed_decks=False)


@pytest.fixture
def client(app):
    return app.test_client()
