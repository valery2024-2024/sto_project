from flask import (
    Blueprint, render_template, request, jsonify, redirect,
    url_for, flash, make_response, session, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity
)
from flask_login import login_required, current_user
from .. import db, login_manager
from ..models import User, Client, Appointment, Booking, Car, ContactMessage
from ..services.email_service import send_email

api_blueprint = Blueprint('api', __name__)

#                           JWT  
@api_blueprint.route('/get_token/<string:email>', methods=['GET'])
def get_token(email):
    user = User.query.filter_by(email=email).first()
    if user:
        token = create_access_token(identity=user.id)
        return jsonify(access_token=token)
    return jsonify({"message": "Користувача не знайдено"}), 404

@api_blueprint.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({"id": user.id, "name": user.name, "email": user.email})

#                        AUTH  
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@api_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        if not name or not email or not password:
            flash("Всі поля є обов'язковими!", "danger")
            return redirect(url_for('api.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Користувач з таким email вже існує!', 'danger')
            return redirect(url_for('api.register'))

        is_first_user = User.query.count() == 0
        new_user = User(name=name, email=email, password=hashed_password, is_admin=is_first_user)
        db.session.add(new_user)
        db.session.commit()
        flash('Реєстрація успішна! Тепер увійдіть', 'success')
        return redirect(url_for('api.login'))
    return render_template('register.html')

@api_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    data = request.get_json(force=True)
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "Користувача не знайдено"}), 404
    if not check_password_hash(user.password, password):
        return jsonify({"msg": "Невірний пароль"}), 401

    access_token = create_access_token(identity=str(user.id))
    response = make_response(jsonify({"access_token": access_token}))
    response.set_cookie("access_token_cookie", access_token, httponly=True)
    return response, 200

@api_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    response = make_response(jsonify({"msg": "Ви вийшли з акаунту."}))
    response.delete_cookie("access_token_cookie")
    flash('Ви вийшли з акаунту.', 'success')
    response.headers['Location'] = url_for('api.home')
    response.status_code = 302
    return response

#                         ПРОФІЛЬ  
@api_blueprint.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify({"id": user.id, "name": user.name, "email": user.email})
    return jsonify({"msg": "Користувача не знайдено"}), 404

@api_blueprint.route('/api/profile', methods=['GET'])
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

@api_blueprint.route('/profile_with_cars')
def profile_with_cars():
    return render_template('profile_with_cars.html')

@api_blueprint.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть у систему!', 'danger')
        return redirect(url_for('api.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not check_password_hash(user.password, current_password):
            flash(' Невірний поточний пароль!', 'danger')
            return redirect(url_for('api.change_password'))

        if new_password != confirm_password:
            flash(' Нові паролі не співпадають!', 'danger')
            return redirect(url_for('api.change_password'))

        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash(' Пароль успішно змінено!', 'success')
        return redirect(url_for('api.profile'))

    return render_template('change_password.html')

#                         HOME  
@api_blueprint.route('/')
def home():
    return render_template('index.html')

@api_blueprint.route('/sto')
def sto():
    return render_template('sto.html')

#                         BOOKING 
@api_blueprint.route('/booking', methods=['GET', 'POST'])
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
        return redirect(url_for('api.booking'))
    return render_template('booking.html')

@api_blueprint.route('/booking/update/<int:booking_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('api.admin'))
    return render_template('update_booking.html', booking=booking)

@api_blueprint.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash("Запис успішно видалено!", "success")
    return redirect(url_for('api.admin'))

#                         CONTACTS 
@api_blueprint.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get("name")
    phone = request.form.get("phone")
    message = request.form.get("message")
    email = request.form.get("email")

    if not name or not phone or not message:
        flash("Всі поля обов’язкові для заповнення!", "error")
        return redirect(url_for("api.home"))

    new_message = ContactMessage(name=name, phone=phone, message=message)
    db.session.add(new_message)
    db.session.commit()
    flash("Дякуємо! Ваша заявка прийнята.", "success")
    return redirect(url_for("api.home"))

@api_blueprint.route('/admin/contacts')
def admin_contacts():
    contacts = ContactMessage.query.all()
    return render_template('admin_contacts.html', contacts=contacts)

@api_blueprint.route('/admin/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    contact = ContactMessage.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash("Повідомлення успішно видалено!", "success")
    return redirect(url_for('api.admin_contacts'))

#                      ADMIN 
@api_blueprint.route('/admin')
def admin():
    bookings = Booking.query.all()
    users = User.query.all()
    return render_template('admin.html', bookings=bookings, users=users)

@api_blueprint.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        flash(' У вас немає доступу!', 'danger')
        return redirect(url_for('api.home'))

    users = User.query.all()
    return render_template('admin_users.html', users=users)
