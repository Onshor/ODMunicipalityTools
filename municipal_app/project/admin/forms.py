# project/admin/forms.py
# -*- coding: utf-8 -*

from flask_wtf import Form
from wtforms import PasswordField
from wtforms.validators import DataRequired, Length, EqualTo


class ChangePwdForm(Form):
    admin_password = PasswordField('password', validators=[DataRequired()])
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )