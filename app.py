from flask import Flask, make_response, render_template, request, redirect, url_for, jsonify, flash, session, send_from_directory
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape
from flask_mail import Message
from app.models import (
    Client,
    Appointment,
    Message,
    Car,
    Booking,
    ContactMessage,
    User,
)
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app.extensions import cors, db, jwt, login_manager, mail, migrate
from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.booking import booking_bp
from app.routes.cars import cars_bp
from app.routes.contact import contact_bp
from app.routes.main import main_bp
from app.routes.profile import profile_bp
import os
import logging

def safe_str_cmp(a, b):
    return a == b

logging.basicConfig(level=logging.DEBUG)
# Конфігурація Flask додатку
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "sto.db")
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"  # База даних SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your_secret_key")
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

# Налаштування Flask-Mail (БЕЗ `MAIL_PASSWORD` в коді)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", "your_email@gmail.com")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", "your_app_password")
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

app.config['JWT_SECRET_KEY'] = 'super-secret'  # Замініти на мій ключ
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']  # Для використання як у заголовках, так і в cookies
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False


# Ініціалізація бази даних та пошти
db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)
jwt.init_app(app)
cors.init_app(app, supports_credentials=True)
login_manager.init_app(app)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(cars_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(main_bp)
app.register_blueprint(profile_bp)

# Функції JWT
def authenticate(email, password): # Модель користувача # зв’язок з авто #Додаємо роль
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return user

def identity(payload):
    user_id = payload['identity']
    return User.query.get(user_id)

@app.route('/get_token/<string:email>', methods=['GET'])
def get_token(email):
    user = User.query.filter_by(email=email).first()
    if user:
        token = create_access_token(identity=user.id)
        return jsonify(access_token=token)
    return jsonify({"message": "Користувача не знайдено"}), 404



# Створення таблиць у БД
with app.app_context():
    db.create_all()

 
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
       current_user_id = get_jwt_identity()
       user = User.query.get(current_user_id)
       return jsonify({"id": user.id, "name": user.name, "email": user.email})

# Де User — моя модель користувача
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

#----------------------Запис Авто------------------------------
# Сторінка запису на ремонт
# -------------------- ФОРМА ЗВОРОТНОГО ЗВ'ЯЗКУ --------------------

# -------------------- ЗАПУСК СЕРВЕРА --------------------
@app.after_request
def add_csp_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "connect-src 'self' http://127.0.0.1:5000;"
    )
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
