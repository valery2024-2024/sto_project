from flask_mail import Message
from .. import mail

def send_email(name, phone, message, recipient):
    msg = Message("Нова заявка на СТО", recipients=[recipient])
    msg.body = f"Ім'я: {name}\nТелефон: {phone}\nПовідомлення: {message}"
    mail.send(msg)