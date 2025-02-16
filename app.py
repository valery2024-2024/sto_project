from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape
from flask_mail import Mail, Message
import os
import logging

logging.basicConfig(level=logging.DEBUG)
# Конфігурація Flask додатку
app = Flask(__name__, static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sto.db'  # База даних SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")

# Налаштування Flask-Mail (БЕЗ `MAIL_PASSWORD` в коді)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", "your_email@gmail.com")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", "your_app_password")
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

# Ініціалізація бази даних та пошти
db = SQLAlchemy(app)
mail = Mail(app)

# -------------------- МОДЕЛІ БД --------------------

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    engine = db.Column(db.Integer, nullable=False)
    fuel_consumption = db.Column(db.Float, nullable=False)
    register = db.Column(db.Boolean, default=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(120), nullable=False)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Модель користувача
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)    

# Створення таблиць у БД
with app.app_context():
    db.create_all()

# -------------------- ГОЛОВНІ МАРШРУТИ --------------------
@app.route('/register', methods=['GET', 'POST']) #Реєстрація нового користувача
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Перевіряємо, чи вже є такий email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Користувач з таким email вже існує!', 'danger')
            return redirect(url_for('register'))

        # Додаємо нового користувача
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Реєстрація успішна! Тепер увійдіть.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST']) #Вхід в систему
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            flash('Ви успішно увійшли!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Невірний email або пароль', 'danger')

    return render_template('login.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/change_password', methods=['GET', 'POST']) #Зміна пароля
def change_password():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть у систему!', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Перевірка старого пароля
        if not check_password_hash(user.password, current_password):
            flash('❌ Невірний поточний пароль!', 'danger')
            return redirect(url_for('change_password'))

        # Перевірка збігу нового пароля
        if new_password != confirm_password:
            flash('❌ Нові паролі не співпадають!', 'danger')
            return redirect(url_for('change_password'))

        # Оновлення пароля
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash('✅ Пароль успішно змінено!', 'success')
        return redirect(url_for('profile'))

    return render_template('change_password.html')

@app.route('/profile') #Особистий кабінет(Профіль)
def profile():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть у систему!', 'danger')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user_name=session.get('user_name', 'Користувач'), user_email=session.get('user_email', ''))

@app.route('/logout') #Вихід із системи
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('Ви вийшли з акаунту.', 'success')
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin():
    bookings = Booking.query.all()
    return render_template('admin.html', bookings=bookings)

@app.route ('/sto')
def sto():
    return render_template('sto.html')

# Сторінка запису на ремонт
@app.route('/booking/update/<int:booking_id>', methods=['GET', 'POST'])
def update_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if request.method == 'POST':
        booking.name = request.form['name']
        booking.phone = request.form['phone']
        booking.date = request.form['date']
        booking.comment = request.form['comment']
        booking.email = request.form['email']

        db.session.commit()
        flash("Запис успішно оновлено!", "success")
        return redirect(url_for('admin'))

    return render_template('update_booking.html', booking=booking)


# -------------------- БРОНЮВАННЯ --------------------

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        new_booking = Booking(
            name=request.form['name'],
            phone=request.form['phone'],
            date=request.form['date'],
            comment=request.form.get('comment', ''),
            email=request.form['email']
        )
        db.session.add(new_booking)
        db.session.commit()
        flash("Запис успішно створено!", "success")
        return redirect(url_for('home'))
    return render_template('booking.html')

@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash("Запис успішно видалено!", "success")
    return redirect(url_for('admin'))

# -------------------- ФОРМА ЗВОРОТНОГО ЗВ'ЯЗКУ --------------------

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get("name")
    phone = request.form.get("phone")
    message = request.form.get("message")

    if not name or not phone or not message:
        flash("Всі поля обов’язкові для заповнення!", "error")
        return redirect(url_for("home"))

    new_message = ContactMessage(name=name, phone=phone, message=message)
    db.session.add(new_message)
    db.session.commit()

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
        print("✅ Email успішно відправлено!")
    except Exception as e:
        print(f"❌ Помилка при відправці email: {e}")

# -------------------- ЗАПУСК СЕРВЕРА --------------------

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

