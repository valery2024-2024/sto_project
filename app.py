from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

# Конфігурація Flask додатку
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sto.db'  # База даних SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ініціалізація бази даних
db = SQLAlchemy(app)

# Модель для збереження записів клієнтів
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(120), unique=True)

# Створення таблиць у базі даних
with app.app_context():
    db.create_all()

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
        comment = request.form['comment']
        email = request.form['email']
        
        # Перевірка на унікальність email
        existing_booking = Booking.query.filter_by(email=email).first()
        if existing_booking:
            return "Користувач із таким email вже записаний!", 400
        
        # Створення нового запису
        new_booking = Booking(name=name, phone=phone, date=date, comment=comment, email=email)
        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('booking.html')

# Адмін-панель для перегляду заявок
@app.route('/admin')
def admin():
    bookings = Booking.query.all()
    return render_template('admin.html', bookings=bookings)

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
    query = request.args.get('query')
    results = Booking.query.filter((Booking.name.contains(query)) | (Booking.phone.contains(query))).all()
    return render_template('search.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
