from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User


def create_user(name="Account User", email="account@example.com", password="old-password"):
    user = User(
        name=name,
        email=email,
        password=generate_password_hash(password, method="pbkdf2:sha256"),
    )
    db.session.add(user)
    db.session.commit()
    return user


def log_in_user(client, user_id, user_name):
    with client.session_transaction() as current_session:
        current_session["user_id"] = user_id
        current_session["user_name"] = user_name


def password_payload(**overrides):
    payload = {
        "current_password": "old-password",
        "new_password": "new-password",
        "confirm_password": "new-password",
    }
    payload.update(overrides)
    return payload


def assert_access_token_cookie_deleted(response):
    set_cookie_headers = response.headers.getlist("Set-Cookie")
    assert any(
        header.startswith("access_token_cookie=")
        and ("Max-Age=0" in header or "expires=Thu, 01 Jan 1970" in header)
        for header in set_cookie_headers
    )


def test_logout_authenticated_user_clears_session_and_jwt_cookie(client):
    log_in_user(client, 1, "Account User")

    response = client.post("/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    assert_access_token_cookie_deleted(response)

    with client.session_transaction() as current_session:
        assert "user_id" not in current_session
        assert "user_name" not in current_session


def test_logout_without_active_session_redirects_without_error(client):
    response = client.post("/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    assert_access_token_cookie_deleted(response)

    with client.session_transaction() as current_session:
        assert "user_id" not in current_session
        assert "user_name" not in current_session


def test_change_password_with_correct_current_password_updates_hash(app, client):
    with app.app_context():
        user = create_user()
        user_id = user.id
        user_name = user.name

    log_in_user(client, user_id, user_name)

    response = client.post("/change_password", data=password_payload())

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/profile_with_cars")

    with app.app_context():
        updated_user = db.session.get(User, user_id)
        assert updated_user.password != "new-password"
        assert not check_password_hash(updated_user.password, "old-password")
        assert check_password_hash(updated_user.password, "new-password")


def test_change_password_with_wrong_current_password_keeps_existing_hash(app, client):
    with app.app_context():
        user = create_user(email="wrong-current@example.com")
        user_id = user.id
        user_name = user.name
        original_hash = user.password

    log_in_user(client, user_id, user_name)

    response = client.post(
        "/change_password",
        data=password_payload(current_password="wrong-password"),
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/change_password")

    with app.app_context():
        unchanged_user = db.session.get(User, user_id)
        assert unchanged_user.password == original_hash
        assert check_password_hash(unchanged_user.password, "old-password")
        assert not check_password_hash(unchanged_user.password, "new-password")


def test_change_password_without_authorization_redirects_and_keeps_password(app, client):
    with app.app_context():
        user = create_user(email="unauthorized-change@example.com")
        user_id = user.id
        original_hash = user.password

    response = client.post("/change_password", data=password_payload())

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    with app.app_context():
        unchanged_user = db.session.get(User, user_id)
        assert unchanged_user.password == original_hash
        assert check_password_hash(unchanged_user.password, "old-password")


def test_change_password_with_mismatched_confirmation_keeps_existing_hash(app, client):
    with app.app_context():
        user = create_user(email="mismatch-change@example.com")
        user_id = user.id
        user_name = user.name
        original_hash = user.password

    log_in_user(client, user_id, user_name)

    response = client.post(
        "/change_password",
        data=password_payload(confirm_password="different-password"),
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/change_password")

    with app.app_context():
        unchanged_user = db.session.get(User, user_id)
        assert unchanged_user.password == original_hash
        assert check_password_hash(unchanged_user.password, "old-password")
        assert not check_password_hash(unchanged_user.password, "new-password")
