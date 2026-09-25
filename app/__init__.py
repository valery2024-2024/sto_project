import logging
import os

from flask import Flask, render_template
from dotenv import load_dotenv

from app.extensions import cors, db, jwt, login_manager, mail, migrate
from app.models import User


load_dotenv()

logging.basicConfig(level=logging.DEBUG)
PACKAGE_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.abspath(os.path.join(PACKAGE_DIR, os.pardir))
DB_PATH = os.path.join(BASE_DIR, "instance", "sto.db")


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", "your_email@gmail.com")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", "your_app_password")
    app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

    app.config['JWT_SECRET_KEY'] = os.environ["JWT_SECRET_KEY"]
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, supports_credentials=True)
    login_manager.init_app(app)

    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.booking import booking_bp
    from app.routes.cars import cars_bp
    from app.routes.contact import contact_bp
    from app.routes.main import main_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(cars_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(profile_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    @app.after_request
    def add_csp_headers(response):
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "connect-src 'self' http://127.0.0.1:5000;"
        )
        return response

    return app
