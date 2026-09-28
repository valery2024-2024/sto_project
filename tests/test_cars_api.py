from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Car, User


def make_user(name, email):
    user = User(
        name=name,
        email=email,
        password=generate_password_hash("secret-password", method="pbkdf2:sha256"),
    )
    db.session.add(user)
    db.session.commit()
    return user


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def valid_car_payload(**overrides):
    payload = {
        "name": "Test Car",
        "engine": 1600,
        "fuel_consumption": 7.5,
        "register": True,
    }
    payload.update(overrides)
    return payload


def test_add_car_without_jwt_is_unauthorized(app, client):
    response = client.post("/api/add_car", json=valid_car_payload())

    assert response.status_code == 401

    with app.app_context():
        assert Car.query.count() == 0


def test_add_car_with_valid_jwt_creates_car_for_user(app, client):
    with app.app_context():
        user = make_user("Car Owner", "owner@example.com")
        token = create_access_token(identity=str(user.id))
        user_id = user.id

    response = client.post(
        "/api/add_car",
        json=valid_car_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    assert response.is_json

    with app.app_context():
        car = Car.query.one()
        assert car.name == "Test Car"
        assert car.engine == 1600
        assert car.fuel_consumption == 7.5
        assert car.register is True
        assert car.user_id == user_id


def test_add_car_belongs_to_user_from_jwt(app, client):
    with app.app_context():
        first_user = make_user("First User", "first-car-owner@example.com")
        second_user = make_user("Second User", "second-car-owner@example.com")
        token = create_access_token(identity=str(first_user.id))
        first_user_id = first_user.id
        second_user_id = second_user.id

    response = client.post(
        "/api/add_car",
        json=valid_car_payload(name="Owned Car"),
        headers=auth_headers(token),
    )

    assert response.status_code == 201

    with app.app_context():
        car = Car.query.one()
        assert car.user_id == first_user_id
        assert car.user_id != second_user_id


def test_add_car_missing_required_fields_returns_400(app, client):
    with app.app_context():
        user = make_user("Validation User", "validation@example.com")
        token = create_access_token(identity=str(user.id))

    response = client.post(
        "/api/add_car",
        json={"name": "Incomplete Car", "engine": 1600},
        headers=auth_headers(token),
    )

    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["msg"].startswith("Missing required fields:")

    with app.app_context():
        assert Car.query.count() == 0


def test_add_car_invalid_numeric_fields_returns_400(app, client):
    with app.app_context():
        user = make_user("Numeric User", "numeric@example.com")
        token = create_access_token(identity=str(user.id))

    response = client.post(
        "/api/add_car",
        json=valid_car_payload(engine="not-a-number"),
        headers=auth_headers(token),
    )

    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["msg"] == "Invalid numeric fields"

    with app.app_context():
        assert Car.query.count() == 0
