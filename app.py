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
from app.routes.auth import auth_bp
from app.routes.booking import booking_bp
from app.routes.cars import cars_bp
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
app.register_blueprint(auth_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(cars_bp)
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

@app.route('/api/contact_message', methods=['POST'])
def contact_message():
    data = request.json
    message = Message(name=data['name'], email=data['email'], message=data['message'])
    db.session.add(message)
    db.session.commit()
    return jsonify({'message': 'Повідомлення надіслано'}), 200

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

#----------------------Запис Авто------------------------------
@app.route('/admin')
def admin():
    bookings = Booking.query.all()
    users = User.query.all()
    return render_template('admin.html', bookings=bookings, users=users)

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        flash('❌ У вас немає доступу!', 'danger')
        return redirect(url_for('main.home'))

    users = User.query.all()
    print(users) # Виведе список у терміналі
    return render_template('admin_users.html', users=users)

@app.route('/api/admin/users', methods=['GET'])
def api_admin_users():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name, "email": user.email, "is_admin": user.is_admin} for user in users])

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get_or_404(user_id)

    if user.id == session['us er_id']:
        return jsonify({"error": "Cannot delete yourself"}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        flash('❌ У вас немає доступу!', 'danger')
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)

    # Захист від видалення себе
    if user.id == session['user_id']:
        flash('❌ Ви не можете видалити свій обліковий запис!', 'danger')
        return redirect(url_for('admin_users'))

    db.session.delete(user)
    db.session.commit()
    flash('✅ Користувач видалений!', 'success')
    return redirect(url_for('admin_users'))

# Сторінка запису на ремонт
# -------------------- ФОРМА ЗВОРОТНОГО ЗВ'ЯЗКУ --------------------

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    try:
        name = request.form.get("name")
        phone = request.form.get("phone")
        message = request.form.get("message")
        email = request.form.get("email")
        # Діагностика: Перевіряємо, чи отримані дані з форми
        print(f"Отримані дані: ім'я={name}, телефон={phone}, повідомлення={message}")

        if not name or not phone or not message:# or not email:
            flash("Всі поля обов’язкові для заповнення!", "error")
            return redirect(url_for("home"))
        
        # Створення нового запису
        new_message = ContactMessage(name=name, phone=phone, message=message)
        db.session.add(new_message)
        db.session.commit()
        print("Запис успішно збережено в базу даних!")
        
        flash("Дякуємо! Ваша заявка прийнята.", "success")
    except Exception as e:
        print(f"Помилка збереження: {e}")
        send_email(name, phone, message)

        flash("Дякуємо! Ваша заявка прийнята, ми зв’яжемося з вами найближчим часом.", "success")
    return redirect(url_for("home"))

@app.route('/admin/contacts')
def admin_contacts():
    contacts = ContactMessage.query.all()
    return render_template('admin_contacts.html', contacts=contacts)

@app.route('/admin/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    contact = ContactMessage.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash("Повідомлення успішно видалено!", "success")
    return redirect(url_for('admin_contacts'))


# -------------------- ФУНКЦІЯ ВІДПРАВКИ EMAIL --------------------

def send_email(name, phone, message):
    try:
        msg = Message("Нова заявка на СТО",
                        recipients=[app.config['MAIL_USERNAME']])
        msg.body = f"Ім'я: {name}\nТелефон: {phone}\nПовідомлення: {message}"
        mail.send(msg)
        print("Email успішно відправлено!")
    except Exception as e:
        print(f"Помилка при відправці email: {e}")

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
