# project/user/forms.py
# -*- coding: utf-8 -*


from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from project.models import User
from list_municipality import municipalitys



class LoginForm(Form):
    email = TextField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])


class RegisterForm(Form):
    email = TextField(
        'email',
        validators=[DataRequired(), Email(message=None), Length(min=6, max=40)])
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
    name = TextField('First Name', validators=[DataRequired(), Length(max=15)])
    last_name = TextField('Last Name', validators=[DataRequired(), Length(max=80)])
    choices = [(None, u'المنطقة البلدية')]
    for _ in municipalitys:
        if _['municipal_id'] != '1':
            choices.append((_['municipal_id'], _['municipal_name_ar']))
    municipal_id = SelectField('Municipality name', validators=[DataRequired()], choices=choices)

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True


class ChangePasswordForm(Form):
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
