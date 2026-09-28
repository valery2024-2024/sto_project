from pathlib import Path


def test_app_factory_uses_testing_config(app, client):
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    production_db = Path("instance/sto.db").resolve()

    assert app.config["TESTING"] is True
    assert "instance/sto.db" not in db_uri.replace("\\", "/")
    assert str(production_db) not in db_uri
    assert app.name == "app"

    response = client.get("/")
    assert response.status_code == 200
