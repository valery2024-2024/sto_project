from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
#from flask_jwt import JWT, jwt_required, current_identity
#from werkzeug.security import safe_str_cmp
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
app.config['JWT_SECRET_KEY'] = 'super-secret'

# Налаштування Flask-Mail (БЕЗ `MAIL_PASSWORD` в коді)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", "your_email@gmail.com")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", "your_app_password")
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

# Ініціалізація бази даних та пошти
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
jwt = JWTManager(app)


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
    is_admin = db.Column(db.Boolean, default=False) #Додаємо роль  

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

# Функції JWT
def authenticate(email, password):
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



#jwt = JWTManager(app)
#with app.app_context():
    #user = User.query.filter_by(email='example@example.com').first()  # Заміни на правильний email
#if user:
   #token = create_access_token(identity=user.id)
#else:
    #print("Перевірка чи працює  Користувача не знайдено.")

# Створення таблиць у БД
with app.app_context():
    db.create_all()

 
# -------------------- ГОЛОВНІ МАРШРУТИ --------------------

#@app.route('/register', methods=['GET', 'POST']) #Реєстрація нового користувача
#def register_user():
    #if request.method == 'POST':
       #name = request.form['name']
       #email = request.form['email']
       #password = request.form['password']
       #hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        

       # Перевіряємо, чи вже є такий email
       #existing_user = User.query.filter_by(email=email).first()
       #if existing_user:
           #flash('Користувач з таким email вже існує!', 'danger')
           #return redirect(url_for('register'))

       # Додаємо нового користувача
       ##is_first_user = User.query.count() == 0
       #new_user = User(name=name, email=email, password=hashed_password, is_admin=is_first_user)
       #db.session.add(new_user)
       #db.session.commit()
       #flash('Реєстрація успішна! Тепер увійдіть.', 'success')
       #return redirect(url_for('login'))

    #return render_template('register.html')



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
            #name = data['name']
        name = data.get('name')
            #email = data['email']
        email = data.get('email')
            #password = data['password']
        password = data.get('password')
        #else:  # Якщо це форма HTML
            #name = request.form['name']
            #email = request.form['email']
            #password = request.form['password']
        if not name or not email or not password:
            flash("Всі поля є обов'язковими!", "danger")
            return redirect(url_for('register'))    


        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Користувач з таким email вже існує!', 'danger')
            return redirect(url_for('register'))
            #return jsonify({"message": "Користувач з таким email вже існує!"}), 400

        is_first_user = User.query.count() == 0
        new_user = User(name=name, email=email, password=hashed_password, is_admin=is_first_user)
        db.session.add(new_user)
        db.session.commit()
        flash('Реєстрація успішна! Тепер увійдіть', 'success')
        return redirect(url_for('login'))

        #if request.is_json:
            #return jsonify({"message": "Користувач зареєстрований!"}), 201
        #else:
            #flash('Реєстрація успішна! Тепер увійдіть.', 'success')
            #return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        email = data.get('email')
        password = data.get('password')
    
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id)

            # ✅ Додаємо користувача в сесію
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email

            print(f"Отримано email: {email}, password: {password}")

            # Якщо це API-запит, повертаємо токен
            if request.is_json:
                return jsonify({"access_token": access_token, "user": user.name}), 200
            
            flash("Вхід успішний!", "success")
            return redirect(url_for("home"))  # Переадресовуємо на головну сторінку
        
        flash("Невірні дані!", "danger")
        return redirect(url_for("login"))
    
    return render_template("login.html")
    #return jsonify({"message": "Невірні дані"}), 401    
    #user = authenticate(data['email'], data['password'])
    #if user:
        #return jsonify({"access_token": user.id, "user": user.name})

#@app.route('/profile')
#@jwt_required()
#def profile_user():
    #return jsonify({"id": current_identity.id, "name": current_identity.name, "email": current_identity.email})

#@app.route('/admin/users')
#@jwt_required()
#def admin_users():
    #user_id = get_jwt_identity()
    #user = User.query.get(user_id)
    #if not user.is_admin:
        #return jsonify({"message": "Недостатньо прав"}), 403
    #if not current_identity.is_admin:
        #return jsonify({"message": "Недостатньо прав"}), 403
    #users = User.query.all()
    #return jsonify([{"id": u.id, "name": u.name, "email": u.email, "is_admin": u.is_admin} for u in users])

#@app.route('/login', methods=['GET', 'POST']) #Вхід в систему
#def login_page():
    #if request.method == 'POST':
       #email = request.form['email']
        #password = request.form['password']
        #user = User.query.filter_by(email=email).first()

        #if user and check_password_hash(user.password, password):
            #session['user_id'] = user.id
            #session['user_name'] = user.name
            #session['user_email'] = user.email
            #session['is_admin'] = user.is_admin  # Додаємо роль
            #flash('Ви успішно увійшли!', 'success')
            #return redirect(url_for('home'))
        #else:
            #flash('Невірний email або пароль', 'danger')

    #return render_template('login.html')


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

#@app.route('/profile') #Особистий кабінет(Профіль)
#def profile_page():
 #   if 'user_id' not in session:
 #       flash('Будь ласка, увійдіть у систему!', 'danger')
#        return redirect(url_for('login'))
 #   user = User.query.get(session['user_id'])
#    return render_template('profile.html', user=user)

#@app.route('/profile')
#@jwt_required()
#def profile():
    #user_id = get_jwt_identity()  # Отримуємо ID користувача з токена
    #user = User.query.get(user_id)  # Завантажуємо користувача з бази даних
    #return jsonify({"id": user.id, "name": user.name, "email": user.email})

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()  # Отримуємо ID користувача з токена
    user = User.query.get(user_id)  # Завантажуємо користувача з бази даних
    if user:
        return jsonify({"id": user.id, "name": user.name, "email": user.email})
    return jsonify({"msg": "Користувача не знайдено"}), 404


# Можливість редагувати профіль
#@app.route('/profile', methods=['GET', 'PUT'])
#@jwt_required()
#def profile():
    #user_id = get_jwt_identity()  # Отримуємо ID користувача з токена
    #user = User.query.get(user_id)  # Завантажуємо користувача з бази даних
    #if request.method == 'GET':
        #return jsonify({"id": user.id, "name": user.name, "email": user.email})
    #elif request.method == 'PUT':
        #data = request.get_json()
        #if 'name' in data:
            #user.name = data['name']
        #if 'password' in data:
           # user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    #db.session.commit()
    #return jsonify({"message": "Profile updated"})
    
    
    
    
    
    #def update_profile():
    #if 'user_id' not in session:
        #return jsonify({"error": "Unauthorized"}), 401

    #user = User.query.get(session['user_id'])
    #data = request.get_json()

    #if 'name' in data:
        #user.name = data['name']
    #if 'password' in data:
       #user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')


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
    email = request.form.get("email")

    if not name or not phone or not message or not email:
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
@app.after_request
def add_csp_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; connect-src 'self' http://127.0.0.1:5000; script-src 'self' 'unsafe-inline';"
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)