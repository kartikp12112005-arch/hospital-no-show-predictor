"""
Shared pytest fixtures.

Every test gets a fresh Flask app instance backed by an isolated,
temporary SQLite database — tests never touch the real
database/hospital.db, and each test starts from a clean slate.
"""

import os
import sys

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app  # noqa: E402


@pytest.fixture
def app(tmp_path):
    """A Flask app instance wired to a temporary, isolated database."""
    db_path = str(tmp_path / "test_hospital.db")
    flask_app = create_app(database_path=db_path)
    flask_app.config.update(TESTING=True)
    yield flask_app


@pytest.fixture
def client(app):
    """A Flask test client for making requests against the app."""
    return app.test_client()


@pytest.fixture
def admin_client(client):
    """A test client that is already logged in as the seeded admin."""
    client.post("/login", data={"username": "admin", "password": "Admin@123"})
    return client


@pytest.fixture
def valid_predict_payload():
    """A realistic, fully valid prediction form payload."""
    return {
        "gender": "F",
        "age": 30,
        "scholarship": 0,
        "hypertension": 0,
        "diabetes": 0,
        "alcoholism": 0,
        "handicap": 0,
        "sms_received": 1,
        "waiting_days": 7,
    }
