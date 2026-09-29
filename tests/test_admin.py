from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User


def create_user(name, email, is_admin=False):
    user = User(
        name=name,
        email=email,
        password=generate_password_hash("secret-password", method="pbkdf2:sha256"),
        is_admin=is_admin,
    )
    db.session.add(user)
    db.session.commit()
    return user


def log_in_user(client, user_id, user_name):
    with client.session_transaction() as current_session:
        current_session["user_id"] = user_id
        current_session["user_name"] = user_name


def test_admin_page_without_session_redirects(client):
    response = client.get("/admin")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_admin_page_with_regular_user_redirects(app, client):
    with app.app_context():
        user = create_user("Regular User", "regular-admin-page@example.com")
        user_id = user.id
        user_name = user.name

    log_in_user(client, user_id, user_name)

    response = client.get("/admin")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_admin_page_with_admin_session_returns_200(app, client):
    with app.app_context():
        admin = create_user("Admin User", "admin-page@example.com", is_admin=True)
        admin_id = admin.id
        admin_name = admin.name

    log_in_user(client, admin_id, admin_name)

    response = client.get("/admin")

    assert response.status_code == 200


def test_admin_users_without_admin_authorization_redirects(client):
    response = client.get("/admin/users")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_admin_users_with_admin_session_returns_users(app, client):
    with app.app_context():
        admin = create_user("Admin User", "admin-users@example.com", is_admin=True)
        target_user = create_user("Listed User", "listed-user@example.com")
        admin_id = admin.id
        admin_name = admin.name
        target_user_email = target_user.email

    log_in_user(client, admin_id, admin_name)

    response = client.get("/admin/users")

    assert response.status_code == 200
    assert target_user_email.encode() in response.data


def test_delete_user_without_admin_authorization_keeps_user(app, client):
    with app.app_context():
        user = create_user("Target User", "target-no-admin@example.com")
        user_id = user.id

    response = client.post(f"/admin/users/delete/{user_id}")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with app.app_context():
        assert db.session.get(User, user_id) is not None


def test_delete_user_with_admin_session_deletes_target_user(app, client):
    with app.app_context():
        admin = create_user("Admin User", "delete-admin@example.com", is_admin=True)
        target_user = create_user("Target User", "delete-target@example.com")
        admin_id = admin.id
        admin_name = admin.name
        target_user_id = target_user.id

    log_in_user(client, admin_id, admin_name)

    response = client.post(f"/admin/users/delete/{target_user_id}")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/users")

    with app.app_context():
        assert db.session.get(User, target_user_id) is None


def test_delete_user_with_admin_session_cannot_delete_self(app, client):
    with app.app_context():
        admin = create_user("Admin User", "self-delete-admin@example.com", is_admin=True)
        admin_id = admin.id
        admin_name = admin.name

    log_in_user(client, admin_id, admin_name)

    response = client.post(f"/admin/users/delete/{admin_id}")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/users")

    with app.app_context():
        assert db.session.get(User, admin_id) is not None


def test_delete_missing_user_with_admin_session_returns_404(app, client):
    with app.app_context():
        admin = create_user("Admin User", "missing-user-admin@example.com", is_admin=True)
        admin_id = admin.id
        admin_name = admin.name

    log_in_user(client, admin_id, admin_name)

    response = client.post("/admin/users/delete/999999")

    assert response.status_code == 404
