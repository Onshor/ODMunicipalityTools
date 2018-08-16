# project/email.py

from flask_mail import Message

from project import app, mail


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=['boltanebochra@gmail.com'] + ['contact@onshor.org'],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


def send_log_email(subject, template):
    msg = Message(
        subject,
        recipients=['med@onshor.org'],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)
