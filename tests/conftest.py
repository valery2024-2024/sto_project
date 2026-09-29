import os
import shutil
import uuid
from pathlib import Path

import pytest

from app import create_app
from app.extensions import db


TEST_TEMP_ROOT = Path(__file__).parent / ".tmp"
TEST_TEMP_ROOT.mkdir(exist_ok=True)
os.environ.setdefault("TMP", str(TEST_TEMP_ROOT))
os.environ.setdefault("TEMP", str(TEST_TEMP_ROOT))
os.environ.setdefault("TMPDIR", str(TEST_TEMP_ROOT))


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(TEST_TEMP_ROOT, ignore_errors=True)


@pytest.fixture
def app():
    test_db_dir = TEST_TEMP_ROOT / f"data-{uuid.uuid4().hex}"
    test_db_dir.mkdir(parents=True, exist_ok=True)
    test_db = test_db_dir / "test.db"
    test_db_uri = f"sqlite:///{test_db}"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": test_db_uri,
        "SECRET_KEY": "test-secret",
        "JWT_SECRET_KEY": "test-jwt-secret-for-pytest-only-key",
        "MAIL_SUPPRESS_SEND": True,
    })

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.session.remove()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()
