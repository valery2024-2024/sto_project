from flask import Flask, make_response, render_template, request, redirect, url_for, jsonify, flash, session, send_from_directory
from flask_login import login_required, current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
import os
import logging

def safe_str_cmp(a, b):
    return a == b

logging.basicConfig(level=logging.DEBUG)
# Конфігурація Flask додатку
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "sto.db")
app = Flask(__name__, static_folder="static")
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

app.config['JWT_SECRET_KEY'] = 'super-secret'  # Замініть на ваш ключ
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']  # Для використання як у заголовках, так і в cookies
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False


# Ініціалізація бази даних та пошти
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True)
login_manager = LoginManager()
login_manager.init_app(app)

# -------------------- МОДЕЛІ БД --------------------
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    appointments = db.relationship('Appointment', backref='client', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    service = db.Column(db.String(100))
    comment = db.Column(db.Text)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    engine = db.Column(db.Integer, nullable=False)
    fuel_consumption = db.Column(db.Float, nullable=False)
    register = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_car_user_id'), nullable=False)
    user = db.relationship('User', backref=db.backref('cars', lazy=True))

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False) 

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:  # Якщо це API-запит
            data = request.get_json()
        else: 
            data = request.form
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        if not name or not email or not password:
            flash("Всі поля є обов'язковими!", "danger")
            return redirect(url_for('register'))    


        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Користувач з таким email вже існує!', 'danger')
            return redirect(url_for('register'))

        is_first_user = User.query.count() == 0
        new_user = User(name=name, email=email, password=hashed_password, is_admin=is_first_user)
        db.session.add(new_user)
        db.session.commit()
        flash('Реєстрація успішна! Тепер увійдіть', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Де User — моя модель користувача
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/profile_with_cars')
def profile_with_cars():
    return render_template('profile_with_cars.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    try:
        data = request.get_json(force=True)
        email = data.get('email')
        password = data.get('password')
        print(f"Отримано email: {email}, пароль: {password}")
    except Exception as e:
        print(f"JSON parsing error: {e}")
        return jsonify({"msg": "Invalid JSON"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        print("Користувача не знайдено")
        return jsonify({"msg": "Користувача не знайдено"}), 404

    if not check_password_hash(user.password, password):
        print("Пароль невірний")
        return jsonify({"msg": "Невірний пароль"}), 401

    try:
        access_token = create_access_token(identity=str(user.id))
        print(f"Токен створено: {access_token}")
        response = make_response(jsonify({"access_token": access_token}))
        response.set_cookie("access_token_cookie", access_token, httponly=True)
        return response, 200
    except Exception as e:
        print(f"Помилка створення токена: {e}")
        return jsonify({"msg": "Token generation error"}), 500


@app.route('/api/add_appointment', methods=['POST'])
def add_appointment():
    data = request.json
    client = Client(name=data['name'], phone=data['phone'], email=data.get('email'))
    db.session.add(client)
    db.session.commit()
    
    appointment = Appointment(
        client_id=client.id,
        date=data['date'],
        time=data['time'],
        service=data['service'],
        comment=data.get('comment', '')
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'message': 'Запис успішно додано'}), 201

@app.route('/api/contact_message', methods=['POST'])
def contact_message():
    data = request.json
    message = Message(name=data['name'], email=data['email'], message=data['message'])
    db.session.add(message)
    db.session.commit()
    return jsonify({'message': 'Повідомлення надіслано'}), 200

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    bookings = Appointment.query.all()
    result = []
    for b in bookings:
        client = Client.query.get(b.client_id)
        result.append({
            'name': client.name,
            'phone': client.phone,
            'date': b.date,
            'time': b.time,
            'service': b.service
        })
    return jsonify(result)

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

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def api_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    

    return jsonify({
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin,
        "cars": [
            {
                "id": car.id,
                "name": car.name,
                "engine": car.engine,
                "fuel_consumption": car.fuel_consumption,
                "register": car.register
            } for car in user.cars
        ]
    })

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user:
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email
        })
    return jsonify({"msg": "Користувача не знайдено"}), 404

#----------------------Запис Авто------------------------------
@app.route('/api/add_car', methods=['GET', 'POST'])
@jwt_required()
def api_add_car():
    user_id = get_jwt_identity()    
    data = request.get_json()

    try:
        new_car = Car(
            name=data['name'],
            engine=int(data['engine']),
            fuel_consumption=float(data['fuel_consumption']),
            register=data.get('register', False),
            user_id=user_id
        )
        db.session.add(new_car)
        db.session.commit()
        return jsonify({"msg": "Автомобіль додано успішно!"}), 201
    except Exception as e:
        return jsonify({"msg": f"Помилка: {str(e)}"}), 400

@app.route('/add_car', methods=['GET'])
def add_car():
    return render_template('add_car.html')    
    
@app.route('/logout',  methods=['GET', 'POST']) #Вихід із системи
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    response = make_response(jsonify({"msg": "Ви вийшли з акаунту."}))
    response.delete_cookie("access_token_cookie")
    flash('Ви вийшли з акаунту.', 'success')
    response.headers['Location'] = url_for('home')  # Перенаправлення на головну
    response.status_code = 302  # Код перенаправлення
    #return redirect(url_for('home'))
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin():
    bookings = Booking.query.all()
    users = User.query.all()
    return render_template('admin.html', bookings=bookings, users=users)

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        flash('❌ У вас немає доступу!', 'danger')
        return redirect(url_for('home'))

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
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)

    # Захист від видалення себе
    if user.id == session['user_id']:
        flash('❌ Ви не можете видалити свій обліковий запис!', 'danger')
        return redirect(url_for('admin_users'))

    db.session.delete(user)
    db.session.commit()
    flash('✅ Користувач видалений!', 'success')
    return redirect(url_for('admin_users'))

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
        return redirect(url_for('booking'))
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
        print("✅ Email успішно відправлено!")
    except Exception as e:
        print(f"❌ Помилка при відправці email: {e}")

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