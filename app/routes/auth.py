from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
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
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Користувач з таким email вже існує!', 'danger')
            return redirect(url_for('auth.register'))

        is_first_user = User.query.count() == 0
        new_user = User(name=name, email=email, password=hashed_password, is_admin=is_first_user)
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception:
            current_app.logger.exception("Помилка реєстрації користувача")
            db.session.rollback()
            flash('Не вдалося зареєструвати користувача. Спробуйте ще раз.', 'danger')
            return redirect(url_for('auth.register'))
        flash('Реєстрація успішна! Тепер увійдіть', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    try:
        data = request.get_json(force=True)
        email = data.get('email')
        password = data.get('password')
    except Exception:
        current_app.logger.exception("Invalid login JSON")
        return jsonify({"msg": "Invalid JSON"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "Користувача не знайдено"}), 404

    if not check_password_hash(user.password, password):
        return jsonify({"msg": "Невірний пароль"}), 401

    try:
        session['user_id'] = user.id
        session['user_name'] = user.name
        access_token = create_access_token(identity=str(user.id))
        response = make_response(jsonify({"access_token": access_token}))
        response.set_cookie("access_token_cookie", access_token, httponly=True)
        return response, 200
    except Exception:
        current_app.logger.exception("Token generation error")
        return jsonify({"msg": "Token generation error"}), 500


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    response = make_response(jsonify({"msg": "Ви вийшли з акаунту."}))
    response.delete_cookie("access_token_cookie")
    flash('Ви вийшли з акаунту.', 'success')
    response.headers['Location'] = url_for('main.home')  # Перенаправлення на головну
    response.status_code = 302  # Код перенаправлення
    #return redirect(url_for('main.home'))
    return response


@auth_bp.route("/change_password", methods=["GET", "POST"])
def change_password():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть у систему!', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        session.pop('user_name', None)
        flash('Будь ласка, увійдіть у систему!', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Перевірка старого пароля
        if not check_password_hash(user.password, current_password):
            flash('❌ Невірний поточний пароль!', 'danger')
            return redirect(url_for('auth.change_password'))

        # Перевірка збігу нового пароля
        if new_password != confirm_password:
            flash('❌ Нові паролі не співпадають!', 'danger')
            return redirect(url_for('auth.change_password'))

        # Оновлення пароля
        try:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
        except Exception:
            current_app.logger.exception("Помилка зміни пароля")
            db.session.rollback()
            flash('Не вдалося змінити пароль. Спробуйте ще раз.', 'danger')
            return redirect(url_for('auth.change_password'))
        flash('✅ Пароль успішно змінено!', 'success')
        return redirect(url_for('profile.profile'))

    return render_template('change_password.html')
