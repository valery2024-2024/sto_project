from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    request,
    url_for,
)
from flask_mail import Message as MailMessage

from app.extensions import db, mail
from app.models import ContactMessage
from app.routes.admin import get_current_admin


contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/submit_contact", methods=["POST"])
def submit_contact():
    name = request.form.get("name")
    phone = request.form.get("phone")
    message = request.form.get("message")

    if not name or not phone or not message:
        flash("Всі поля обов’язкові для заповнення!", "error")
        return redirect(url_for("main.home"))

    try:
        # Створення нового запису
        new_message = ContactMessage(name=name, phone=phone, message=message)
        db.session.add(new_message)
        db.session.commit()
    except Exception:
        current_app.logger.exception("Помилка збереження заявки")
        db.session.rollback()
        flash("Не вдалося зберегти заявку. Спробуйте ще раз.", "error")
        return redirect(url_for("main.home"))

    email_sent = send_email(name, phone, message)

    if email_sent:
        flash("Дякуємо! Ваша заявка прийнята.", "success")
    else:
        flash(
            "Дякуємо! Ваша заявка прийнята. Ми зв’яжемося з вами найближчим часом.",
            "success",
        )
    return redirect(url_for("main.home"))


@contact_bp.route("/admin/contacts/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    if not get_current_admin():
        flash("❌ У вас немає доступу!", "danger")
        return redirect(url_for("main.home"))

    contact = ContactMessage.query.get_or_404(contact_id)
    try:
        db.session.delete(contact)
        db.session.commit()
    except Exception:
        current_app.logger.exception("Помилка видалення повідомлення")
        db.session.rollback()
        flash("Не вдалося видалити повідомлення. Спробуйте ще раз.", "error")
        return redirect(url_for("admin.admin"))
    flash("Повідомлення успішно видалено!", "success")
    return redirect(url_for('admin.admin'))


def send_email(name, phone, message):
    try:
        msg = MailMessage("Нова заявка на СТО",
                        recipients=[current_app.config['MAIL_USERNAME']])
        msg.body = f"Ім'я: {name}\nТелефон: {phone}\nПовідомлення: {message}"
        mail.send(msg)
        return True
    except Exception:
        current_app.logger.exception("Помилка при відправці email")
        return False
