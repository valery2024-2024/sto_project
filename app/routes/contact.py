from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_mail import Message as MailMessage

from app.extensions import db, mail
from app.models import ContactMessage, Message


contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/api/contact_message", methods=["POST"])
def contact_message():
    data = request.json
    message = Message(name=data['name'], email=data['email'], message=data['message'])
    db.session.add(message)
    db.session.commit()
    return jsonify({'message': 'Повідомлення надіслано'}), 200


@contact_bp.route("/submit_contact", methods=["POST"])
def submit_contact():
    name = request.form.get("name")
    phone = request.form.get("phone")
    message = request.form.get("message")
    email = request.form.get("email")
    # Діагностика: Перевіряємо, чи отримані дані з форми
    print(f"Отримані дані: ім'я={name}, телефон={phone}, повідомлення={message}")

    if not name or not phone or not message:# or not email:
        flash("Всі поля обов’язкові для заповнення!", "error")
        return redirect(url_for("main.home"))

    try:
        # Створення нового запису
        new_message = ContactMessage(name=name, phone=phone, message=message)
        db.session.add(new_message)
        db.session.commit()
        print("Запис успішно збережено в базу даних!")
    except Exception as e:
        print(f"Помилка збереження: {e}")
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


@contact_bp.route("/admin/contacts")
def admin_contacts():
    contacts = ContactMessage.query.all()
    return render_template('admin_contacts.html', contacts=contacts)


@contact_bp.route("/admin/contacts/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    contact = ContactMessage.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash("Повідомлення успішно видалено!", "success")
    return redirect(url_for('contact.admin_contacts'))


def send_email(name, phone, message):
    try:
        msg = MailMessage("Нова заявка на СТО",
                        recipients=[current_app.config['MAIL_USERNAME']])
        msg.body = f"Ім'я: {name}\nТелефон: {phone}\nПовідомлення: {message}"
        mail.send(msg)
        print("Email успішно відправлено!")
        return True
    except Exception as e:
        print(f"Помилка при відправці email: {e}")
        return False
