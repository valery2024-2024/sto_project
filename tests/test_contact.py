from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import ContactMessage, User
import app.routes.contact as contact_routes


def contact_payload(**overrides):
    payload = {
        "name": "Contact User",
        "phone": "+380501234567",
        "message": "Please call me back",
    }
    payload.update(overrides)
    return payload


def create_contact_message(**overrides):
    contact = ContactMessage(**contact_payload(**overrides))
    db.session.add(contact)
    db.session.commit()
    return contact


def create_admin_user():
    admin = User(
        name="Admin User",
        email="admin-contact@example.com",
        password=generate_password_hash("secret-password", method="pbkdf2:sha256"),
        is_admin=True,
    )
    db.session.add(admin)
    db.session.commit()
    return admin


def log_in_admin(client, admin):
    with client.session_transaction() as current_session:
        current_session["user_id"] = admin.id
        current_session["user_name"] = admin.name


def test_submit_contact_creates_message_and_sends_email(app, client, monkeypatch):
    sent_messages = []

    def fake_send_email(name, phone, message):
        sent_messages.append({
            "name": name,
            "phone": phone,
            "message": message,
        })
        return True

    monkeypatch.setattr(contact_routes, "send_email", fake_send_email)

    response = client.post("/submit_contact", data=contact_payload())

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    assert sent_messages == [contact_payload()]

    with app.app_context():
        contact = ContactMessage.query.one()
        assert contact.name == "Contact User"
        assert contact.phone == "+380501234567"
        assert contact.message == "Please call me back"


def test_submit_contact_missing_required_field_redirects_without_creating_message(
    app,
    client,
    monkeypatch,
):
    def fail_if_called(name, phone, message):
        raise AssertionError("send_email should not be called for invalid contact data")

    monkeypatch.setattr(contact_routes, "send_email", fail_if_called)
    payload = contact_payload()
    payload.pop("message")

    response = client.post("/submit_contact", data=payload)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with app.app_context():
        assert ContactMessage.query.count() == 0


def test_delete_contact_without_admin_redirects_and_keeps_message(app, client):
    with app.app_context():
        contact = create_contact_message()
        contact_id = contact.id

    response = client.post(f"/admin/contacts/delete/{contact_id}")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with app.app_context():
        assert db.session.get(ContactMessage, contact_id) is not None


def test_delete_contact_with_admin_session_deletes_message(app, client):
    with app.app_context():
        admin = create_admin_user()
        contact = create_contact_message()
        admin_id = admin.id
        contact_id = contact.id

    with app.app_context():
        admin = db.session.get(User, admin_id)
        log_in_admin(client, admin)

    response = client.post(f"/admin/contacts/delete/{contact_id}")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin")

    with app.app_context():
        assert db.session.get(ContactMessage, contact_id) is None


def test_delete_missing_contact_with_admin_session_returns_404(app, client):
    with app.app_context():
        admin = create_admin_user()
        admin_id = admin.id

    with app.app_context():
        admin = db.session.get(User, admin_id)
        log_in_admin(client, admin)

    response = client.post("/admin/contacts/delete/999999")

    assert response.status_code == 404
