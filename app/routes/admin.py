from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for

from app.extensions import db
from app.models import Booking, ContactMessage, User
from app.utils.auth import get_current_admin


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
def admin():
    if not get_current_admin():
        flash('❌ У вас немає доступу!', 'danger')
        return redirect(url_for('main.home'))

    bookings = Booking.query.all()
    users = User.query.all()
    contacts = ContactMessage.query.all()
    return render_template('admin.html', bookings=bookings, users=users, contacts=contacts)


@admin_bp.route("/admin/users")
def admin_users():
    if not get_current_admin():
        flash('❌ У вас немає доступу!', 'danger')
        return redirect(url_for('main.home'))

    users = User.query.all()
    return render_template('admin_users.html', users=users)


@admin_bp.route("/admin/users/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if not get_current_admin():
        flash('❌ У вас немає доступу!', 'danger')
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)

    # Захист від видалення себе
    if user.id == session['user_id']:
        flash('❌ Ви не можете видалити свій обліковий запис!', 'danger')
        return redirect(url_for('admin.admin_users'))

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception:
        current_app.logger.exception("Помилка видалення користувача")
        db.session.rollback()
        flash('❌ Не вдалося видалити користувача. Спробуйте ще раз.', 'danger')
        return redirect(url_for('admin.admin_users'))

    flash('✅ Користувач видалений!', 'success')
    return redirect(url_for('admin.admin_users'))
