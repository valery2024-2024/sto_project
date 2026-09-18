from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from app.extensions import db
from app.models import Appointment, Booking, Client


booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/api/add_appointment", methods=["POST"])
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


@booking_bp.route("/api/bookings", methods=["GET"])
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


@booking_bp.route("/booking/update/<int:booking_id>", methods=["GET", "POST"])
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


@booking_bp.route("/booking", methods=["GET", "POST"])
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
        return redirect(url_for('booking.booking'))
    return render_template('booking.html')


@booking_bp.route("/delete_booking/<int:booking_id>", methods=["POST"])
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash("Запис успішно видалено!", "success")
    return redirect(url_for('admin'))
