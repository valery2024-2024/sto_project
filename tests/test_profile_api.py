from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User


def make_user(name, email, is_admin=False):
    user = User(
        name=name,
        email=email,
        password=generate_password_hash("secret-password", method="pbkdf2:sha256"),
        is_admin=is_admin,
    )
    db.session.add(user)
    db.session.commit()
    return user


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_profile_without_jwt_is_unauthorized(client):
    response = client.get("/api/profile")

    assert response.status_code == 401
    assert response.is_json
    assert "name" not in response.get_json()
    assert "email" not in response.get_json()
    assert "cars" not in response.get_json()


def test_profile_with_valid_jwt_returns_user_data(app, client):
    with app.app_context():
        user = make_user(
            name="Profile User",
            email="profile@example.com",
            is_admin=True,
        )
        token = create_access_token(identity=str(user.id))

    response = client.get("/api/profile", headers=auth_headers(token))

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Profile User"
    assert data["email"] == "profile@example.com"
    assert data["is_admin"] is True


def test_profile_uses_jwt_identity_for_current_user(app, client):
    with app.app_context():
        first_user = make_user(
            name="First User",
            email="first@example.com",
            is_admin=False,
        )
        make_user(
            name="Second User",
            email="second@example.com",
            is_admin=True,
        )
        token = create_access_token(identity=str(first_user.id))

    response = client.get("/api/profile", headers=auth_headers(token))

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "First User"
    assert data["email"] == "first@example.com"
    assert data["is_admin"] is False


def test_profile_returns_empty_cars_for_user_without_cars(app, client):
    with app.app_context():
        user = make_user(
            name="No Cars User",
            email="no-cars@example.com",
        )
        token = create_access_token(identity=str(user.id))

    response = client.get("/api/profile", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.get_json()["cars"] == []
