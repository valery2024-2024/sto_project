import os
from flask import Flask

from .config import Config
from app.extensions import (
    cors,
    db,
    jwt,
    login_manager,
    mail,
    migrate,
)

def create_app():
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app, supports_credentials=True)

    from .api.routes import api_blueprint
    app.register_blueprint(api_blueprint)

    return app








    
