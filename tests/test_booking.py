from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Booking, User


def booking_payload(**overrides):
    payload = {
        "name": "Booking User",
        "phone": "+380501112233",
        "date": "2026-10-15",
        "comment": "Need diagnostics",
        "email": "booking@example.com",
    }
    payload.update(overrides)
    return payload


def create_booking(**overrides):
    booking = Booking(**booking_payload(**overrides))
    db.session.add(booking)
    db.session.commit()
    return booking


def create_admin_user():
    admin = User(
        name="Admin User",
        email="admin@example.com",
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


def test_booking_post_creates_booking(app, client):
    response = client.post("/booking", data=booking_payload())

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/booking")

    with app.app_context():
        booking = Booking.query.one()
        assert booking.name == "Booking User"
        assert booking.phone == "+380501112233"
        assert booking.date == "2026-10-15"
        assert booking.comment == "Need diagnostics"
        assert booking.email == "booking@example.com"


def test_booking_post_missing_required_field_returns_400(app, client):
    payload = booking_payload()
    payload.pop("email")

    response = client.post("/booking", data=payload)

    assert response.status_code == 400

    with app.app_context():
        assert Booking.query.count() == 0


def test_update_booking_without_admin_redirects_and_does_not_change(app, client):
    with app.app_context():
        booking = create_booking(name="Original Name", comment="Original comment")
        booking_id = booking.id

    response = client.post(
        f"/booking/update/{booking_id}",
        data=booking_payload(name="Changed Name", comment="Changed comment"),
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with app.app_context():
        unchanged_booking = db.session.get(Booking, booking_id)
        assert unchanged_booking.name == "Original Name"
        assert unchanged_booking.comment == "Original comment"


def test_delete_booking_without_admin_redirects_and_keeps_booking(app, client):
    with app.app_context():
        booking = create_booking()
        booking_id = booking.id

    response = client.post(f"/delete_booking/{booking_id}")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with app.app_context():
        assert db.session.get(Booking, booking_id) is not None


def test_update_booking_with_admin_session_updates_booking(app, client):
    with app.app_context():
        admin = create_admin_user()
        booking = create_booking(name="Before Update", email="before@example.com")
        admin_id = admin.id
        booking_id = booking.id

    with app.app_context():
        admin = db.session.get(User, admin_id)
        log_in_admin(client, admin)

    response = client.post(
        f"/booking/update/{booking_id}",
        data=booking_payload(
            name="After Update",
            phone="+380509998877",
            date="2026-11-20",
            comment="Updated comment",
            email="after@example.com",
        ),
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin")

    with app.app_context():
        updated_booking = db.session.get(Booking, booking_id)
        assert updated_booking.name == "After Update"
        assert updated_booking.phone == "+380509998877"
        assert updated_booking.date == "2026-11-20"
        assert updated_booking.comment == "Updated comment"
        assert updated_booking.email == "after@example.com"


def test_delete_booking_with_admin_session_deletes_booking(app, client):
    with app.app_context():
        admin = create_admin_user()
        booking = create_booking()
        admin_id = admin.id
        booking_id = booking.id

    with app.app_context():
        admin = db.session.get(User, admin_id)
        log_in_admin(client, admin)

    response = client.post(f"/delete_booking/{booking_id}")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin")

    with app.app_context():
        assert db.session.get(Booking, booking_id) is None


def test_update_missing_booking_with_admin_session_returns_404(app, client):
    with app.app_context():
        admin = create_admin_user()
        admin_id = admin.id

    with app.app_context():
        admin = db.session.get(User, admin_id)
        log_in_admin(client, admin)

    response = client.get("/booking/update/999999")

    assert response.status_code == 404
