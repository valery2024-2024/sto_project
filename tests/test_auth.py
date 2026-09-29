from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User


def test_register_creates_user_with_hashed_password(app, client):
    response = client.post("/register", data={
        "name": "Test User",
        "email": "test@example.com",
        "password": "secret-password",
    })

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    with app.app_context():
        user = User.query.filter_by(email="test@example.com").one()
        assert user.email == "test@example.com"
        assert user.password != "secret-password"
        assert check_password_hash(user.password, "secret-password")


def test_register_duplicate_email_does_not_create_second_user(app, client):
    with app.app_context():
        user = User(
            name="Existing User",
            email="existing@example.com",
            password=generate_password_hash("secret-password", method="pbkdf2:sha256"),
        )
        db.session.add(user)
        db.session.commit()

    response = client.post("/register", data={
        "name": "Duplicate User",
        "email": "existing@example.com",
        "password": "other-password",
    })

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/register")

    with app.app_context():
        assert User.query.filter_by(email="existing@example.com").count() == 1


def test_login_returns_token_cookie_and_sets_session(app, client):
    with app.app_context():
        user = User(
            name="Login User",
            email="login@example.com",
            password=generate_password_hash("secret-password", method="pbkdf2:sha256"),
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    response = client.post("/login", json={
        "email": "login@example.com",
        "password": "secret-password",
    })

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()["access_token"]
    assert "access_token_cookie=" in response.headers["Set-Cookie"]
    assert "HttpOnly" in response.headers["Set-Cookie"]

    with client.session_transaction() as current_session:
        assert current_session["user_id"] == user_id
        assert current_session["user_name"] == "Login User"


def test_login_wrong_password_returns_401_without_session(app, client):
    with app.app_context():
        user = User(
            name="Wrong Password User",
            email="wrong-password@example.com",
            password=generate_password_hash("secret-password", method="pbkdf2:sha256"),
        )
        db.session.add(user)
        db.session.commit()

    response = client.post("/login", json={
        "email": "wrong-password@example.com",
        "password": "bad-password",
    })

    assert response.status_code == 401
    assert response.is_json
    assert "access_token" not in response.get_json()

    with client.session_transaction() as current_session:
        assert "user_id" not in current_session
        assert "user_name" not in current_session


def test_login_unknown_user_returns_404_without_session(client):
    response = client.post("/login", json={
        "email": "missing@example.com",
        "password": "secret-password",
    })

    assert response.status_code == 404
    assert response.is_json
    assert "access_token" not in response.get_json()

    with client.session_transaction() as current_session:
        assert "user_id" not in current_session
        assert "user_name" not in current_session
