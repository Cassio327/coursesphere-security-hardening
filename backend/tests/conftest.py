import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from endpoints import create_app


@pytest.fixture
def app():
    application = create_app(
        {
            "TESTING": True,
            "CORS_ALLOWED_ORIGINS": ["http://allowed.test"],
            "CREATE_USER_RATE_LIMIT": 2,
            "CREATE_USER_RATE_WINDOW": 60,
        }
    )
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def valid_authorization():
    return {"Authorization": "Bearer test-token-not-a-secret"}
