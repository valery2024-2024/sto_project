from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.extensions import db
from app.models import Booking
from app.utils.auth import get_current_admin


booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/booking/update/<int:booking_id>", methods=["GET", "POST"])
def update_booking(booking_id):
    if not get_current_admin():
        flash('вќЊ РЈ РІР°СЃ РЅРµРјР°С” РґРѕСЃС‚СѓРїСѓ!', 'danger')
        return redirect(url_for('main.home'))

    booking = Booking.query.get_or_404(booking_id)
    if request.method == 'POST':
        booking.name = request.form['name']
        booking.phone = request.form['phone']
        booking.date = request.form['date']
        booking.comment = request.form['comment']
        booking.email = request.form['email']

        try:
            db.session.commit()
        except Exception:
            current_app.logger.exception("РџРѕРјРёР»РєР° РѕРЅРѕРІР»РµРЅРЅСЏ Р·Р°РїРёСЃСѓ")
            db.session.rollback()
            flash("РќРµ РІРґР°Р»РѕСЃСЏ РѕРЅРѕРІРёС‚Рё Р·Р°РїРёСЃ. РЎРїСЂРѕР±СѓР№С‚Рµ С‰Рµ СЂР°Р·.", "danger")
            return redirect(url_for('admin.admin'))
        flash("Запис успішно оновлено!", "success")
        return redirect(url_for('admin.admin'))

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
        try:
            db.session.add(new_booking)
            db.session.commit()
        except Exception:
            current_app.logger.exception("Помилка створення запису")
            db.session.rollback()
            flash("Не вдалося створити запис. Спробуйте ще раз.", "error")
            return redirect(url_for('booking.booking'))
        flash("Запис успішно створено!", "success")
        return redirect(url_for('booking.booking'))
    return render_template('booking.html')


@booking_bp.route("/delete_booking/<int:booking_id>", methods=["POST"])
def delete_booking(booking_id):
    if not get_current_admin():
        flash('❌ У вас немає доступу!', 'danger')
        return redirect(url_for('main.home'))

    booking = Booking.query.get_or_404(booking_id)
    try:
        db.session.delete(booking)
        db.session.commit()
    except Exception:
        current_app.logger.exception("Помилка видалення запису")
        db.session.rollback()
        flash("Не вдалося видалити запис. Спробуйте ще раз.", "danger")
        return redirect(url_for('admin.admin'))
    flash("Запис успішно видалено!", "success")
    return redirect(url_for('admin.admin'))
