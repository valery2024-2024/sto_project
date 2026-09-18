from flask import Blueprint, flash, jsonify, redirect, render_template, session, url_for

from app.extensions import db
from app.models import Booking, User


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
def admin():
    bookings = Booking.query.all()
    users = User.query.all()
    return render_template('admin.html', bookings=bookings, users=users)


@admin_bp.route("/admin/users")
def admin_users():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        flash('❌ У вас немає доступу!', 'danger')
        return redirect(url_for('main.home'))

    users = User.query.all()
    print(users) # Виведе список у терміналі
    return render_template('admin_users.html', users=users)


@admin_bp.route("/api/admin/users", methods=["GET"])
def api_admin_users():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name, "email": user.email, "is_admin": user.is_admin} for user in users])


@admin_bp.route("/admin/users/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get_or_404(user_id)

    if user.id == session['user_id']:
        return jsonify({"error": "Cannot delete yourself"}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})


@admin_bp.route("/admin/users/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        flash('❌ У вас немає доступу!', 'danger')
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)

    # Захист від видалення себе
    if user.id == session['user_id']:
        flash('❌ Ви не можете видалити свій обліковий запис!', 'danger')
        return redirect(url_for('admin.admin_users'))

    db.session.delete(user)
    db.session.commit()
    flash('✅ Користувач видалений!', 'success')
    return redirect(url_for('admin.admin_users'))
