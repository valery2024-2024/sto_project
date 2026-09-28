def test_home_page_returns_200(client):
    response = client.get("/")

    assert response.status_code == 200


def test_sto_page_returns_200(client):
    response = client.get("/sto")

    assert response.status_code == 200


def test_booking_page_returns_200(client):
    response = client.get("/booking")

    assert response.status_code == 200


def test_login_page_returns_200(client):
    response = client.get("/login")

    assert response.status_code == 200


def test_register_page_returns_200(client):
    response = client.get("/register")

    assert response.status_code == 200


def test_profile_with_cars_page_returns_200(client):
    response = client.get("/profile_with_cars")

    assert response.status_code == 200


def test_add_car_page_returns_200(client):
    response = client.get("/add_car")

    assert response.status_code == 200


def test_unknown_page_returns_custom_404(client):
    response = client.get("/this-page-does-not-exist")

    assert response.status_code == 404
    assert b"404" in response.data
