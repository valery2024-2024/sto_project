from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
from flask_mail import Mail, Message


# Конфігурація Flask додатку
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sto.db'  # База даних SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key' #Потрібен для flash-повідомлень
# Налаштування Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Пошта SMTP (Google)
app.config['MAIL_PORT'] = 587  # Порт SMTP
app.config['MAIL_USE_TLS'] = True  # Використовуємо шифрування
app.config['MAIL_USERNAME'] = 'sof20b13@gmail.com'  # Твій email
app.config['MAIL_PASSWORD'] = '47738848'  # Пароль або App Password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'  # Від кого надсилається


# Ініціалізація бази даних
db = SQLAlchemy(app)
mail = Mail(app)

# Модель для збереження даних про автомобілі
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    engine = db.Column(db.Integer, nullable=False)
    fuel_consumption = db.Column(db.Float, nullable=False)
    register = db.Column(db.Boolean, default=False)

# Модель для збереження записів клієнтів
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(120), nullable=False)

# Створення таблиць у базі даних
with app.app_context():
    db.create_all()

# -------------------- РОБОТА З АВТОМОБІЛЯМИ --------------------

# Список автомобілів
@app.route('/cars', methods=['GET'])
def list_cars():
    cars = Car.query.all()
    return render_template('cars.html', cars=cars)

# Додавання нового автомобіля
@app.route('/cars/add', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        name = request.form['name']
        engine = request.form['engine']
        fuel_consumption = request.form['fuel_consumption']
        register = 'register' in request.form
        new_car = Car(name=name, engine=int(engine), fuel_consumption=float(fuel_consumption), register=register)
        db.session.add(new_car)
        db.session.commit()
        return redirect(url_for('list_cars'))
    return render_template('add_car.html')

# Оновлення даних автомобіля
@app.route('/cars/update/<int:car_id>', methods=['GET', 'POST'])
def update_car(car_id):
    car = Car.query.get_or_404(car_id)
    if request.method == 'POST':
        car.name = request.form['name']
        car.engine = int(request.form['engine'])
        car.fuel_consumption = float(request.form['fuel_consumption'])
        car.register = 'register' in request.form
        db.session.commit()
        return redirect(url_for('list_cars'))
    return render_template('update_car.html', car=car)

# Видалення автомобіля
@app.route('/cars/delete/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    try:
        car = Car.query.get_or_404(car_id)
        db.session.delete(car)
        db.session.commit()
        flash("Автомобіль успішно видалено!", "success") # Повідомлення про успішне видалення
    except Exception as e:
        flash(f"Помилка при видаленні: {e}", "danger") # Повідомлення про помилку
    return redirect(url_for('list_cars'))

# -------------------- РОБОТА З БРОНЮВАННЯМ --------------------

# Головна сторінка
@app.route('/')
def home():
    return render_template('index.html')

# Сторінка запису на ремонт
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        date = request.form['date']
        comment = request.form.get('comment', '')  # Додано значення за замовчуванням
        email = request.form['email']

        # Додаємо запис до бази даних
        new_booking = Booking(name=name, phone=phone, date=date, comment=comment, email=email)
        db.session.add(new_booking)
        db.session.commit()
        flash("Запис успішно створено!", "success")
        return redirect(url_for('home'))

    return render_template('booking.html')

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

# Адмін-панель для перегляду заявок
@app.route('/admin')
def admin():
    bookings = Booking.query.all()
    return render_template('admin.html', bookings=bookings)

# Видалення заявки з бази даних
@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        flash("Запис успішно видалено!", "success")  # Повідомлення про успішне видалення
    except Exception as e:
        flash(f"Помилка при видаленні: {e}", "danger")  # Повідомлення про помилку
    return redirect(url_for('admin'))


# API для отримання заявок
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    bookings = Booking.query.all()
    return jsonify([{
        "id": booking.id,
        "name": booking.name,
        "phone": booking.phone,
        "date": booking.date,
        "comment": booking.comment,
        "email": booking.email
    } for booking in bookings])

# Пошук заявок
@app.route('/search', methods=['GET'])
def search():
    query = escape(request.args.get('query'))
    results = Booking.query.filter((Booking.name.contains(query)) | (Booking.phone.contains(query))).all()
    return render_template('search.html', results=results)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# -------------------- ФОРМА ЗВОРОТНОГО ЗВ'ЯЗКУ --------------------

# Модель для збереження повідомлень з форми
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Створення таблиці для контактів
with app.app_context():
    db.create_all()

# Обробник форми зворотного зв'язку
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get("name")
    phone = request.form.get("phone")
    message = request.form.get("message")

    if not name or not phone or not message:
        flash("Всі поля обов’язкові для заповнення!", "error")
        return redirect(url_for("home"))

    # Збереження в базу даних
    new_message = ContactMessage(name=name, phone=phone, message=message)
    db.session.add(new_message)
    db.session.commit()

    flash("Дякуємо! Ваша заявка прийнята, ми зв’яжемося з вами найближчим часом.", "success")
    return redirect(url_for("home"))

# Сторінка для перегляду контактних заявок
@app.route('/admin/contacts')
def admin_contacts():
    contacts = ContactMessage.query.all()
    return render_template('admin_contacts.html', contacts=contacts)

# Видалення повідомлення
@app.route('/admin/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    try:
        contact = ContactMessage.query.get_or_404(contact_id)
        db.session.delete(contact)
        db.session.commit()
        flash("Повідомлення успішно видалено!", "success")
    except Exception as e:
        flash(f"Помилка при видаленні: {e}", "danger")
    return redirect(url_for('admin_contacts'))

def send_email(name, phone, message):
    try:
        msg = Message("Нова заявка на СТО",
                      recipients=["sof20b13@gmail.com"])  # Вкажи email адміністратора
        msg.body = f"Ім'я: {name}\nТелефон: {phone}\nПовідомлення: {message}"
        mail.send(msg)
        print("✅ Email успішно відправлено!")
    except Exception as e:
        print(f"❌ Помилка при відправці email: {e}")

    @app.route('/submit_contact', methods=['POST'])
    def submit_contact():
        name = request.form.get("name")
        phone = request.form.get("phone")
        message = request.form.get("message")

        if not name or not phone or not message:
            flash("Всі поля обов’язкові для заповнення!", "error")
            return redirect(url_for("home"))

        # Збереження в базу даних
        new_message = ContactMessage(name=name, phone=phone, message=message)
        db.session.add(new_message)
        db.session.commit()

        # Відправка email адміну
        send_email(name, phone, message)

        flash("Дякуємо! Ваша заявка прийнята, ми зв’яжемося з вами найближчим часом.", "success")
        return redirect(url_for("home"))




# -------------------- ЗАПУСК СЕРВЕРА --------------------

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
