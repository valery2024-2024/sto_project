from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

@app.route('/test')
def test():
    return render_template('test.html')

# Налаштування бази даних
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sto.db'  # База даних SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель для збереження записів клієнтів
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text, nullable=True)

# Ініціалізація бази даних
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
        
        # Створення нового запису
        new_booking = Booking(name=name, phone=phone, date=date, comment=comment)
        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for('home'))
    import os
    print("Current working directory:", os.getcwd())
    print("Templates path:", os.path.abspath('templates'))
    print("Templates files:", os.listdir('templates'))

    return render_template('booking.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
