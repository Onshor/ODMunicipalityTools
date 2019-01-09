# project/user/forms.py
# -*- coding: utf-8 -*


from flask_wtf import Form
from wtforms import TextField, PasswordField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from project.models import User


class LoginForm(Form):
    email = TextField('email', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Email()])
    password = PasswordField('password', validators=[DataRequired(message=u'هذه الخانة اجباريه')])


class RegisterForm(Form):
    phone_number = IntegerField(validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    work_position = TextField(validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    email = TextField(
        'email',
        validators=[DataRequired(message=u'هذه الخانة اجباريه'), Email(message=None), Length(min=6, max=40)])
    password = PasswordField(
        'password',
        validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(message=u'هذه الخانة اجباريه'),
            EqualTo('password', message=u'الكلمة السريه يجب ان تتطابق')
        ]
    )
    name = TextField('First Name', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(max=15)])
    last_name = TextField('Last Name', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(max=80)])
    municipal_id = TextField('Municipality name', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(max=80)])

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append(u"البريد الإلكتروني مسجل مسبقا")
            return False
        return True


class ChangePasswordForm(Form):
    password = PasswordField(
        'password',
        validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(message=u'هذه الخانة اجباريه'),
            EqualTo('password', message=u'كلمة السريه يجب ان تتطابق.')
        ]
    )


class ApiForm(Form):
    api_key = TextField('api_key', validators=[DataRequired(message=u'هذه الخانة اجباريه')])


class ContactForm(Form):
    name = TextField('name', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    municipalite = TextField('municipalite', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    email = TextField('email', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Email()])
    tel = IntegerField('tel', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    message = TextAreaField('message')
