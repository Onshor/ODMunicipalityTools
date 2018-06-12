# project/email.py

from flask_mail import Message

from project import app, mail


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to] + ['contact@onshor.org'],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)
