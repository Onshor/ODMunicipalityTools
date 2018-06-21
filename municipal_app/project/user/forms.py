# project/user/forms.py
# -*- coding: utf-8 -*


from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


from project.models import User, Municipality


# def validate_municipality_choice(form, field):
#     print(field.data)
#     if field.data == None:
#         raise ValidationError(u'yo')


class LoginForm(Form):
    email = TextField('email', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Email()])
    password = PasswordField('password', validators=[DataRequired(message=u'هذه الخانة اجباريه')])


class RegisterForm(Form):
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
    choices = [(None, u'المنطقة البلدية')]
    choices.extend([(_.municipal_id, _.municipal_name_ar + ' ' + _.municipal_name) for _ in Municipality.query.filter_by(approved=True).all() if _.municipal_id != '1'])
    municipal_id = SelectField('Municipality name', validators=[DataRequired(message=u'هذه الخانة اجباريه')], choices=sorted(choices, key=lambda tup: tup[0]))

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


class ContactForm(Form):
    name = TextField('name', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    municipalite = TextField('municipalite', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    email = TextField('email', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Email()])
    tel = IntegerField('tel', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    message = TextAreaField('message')



# def validate_municipal_id(form, field):
#     panned_list = [_.municipal_id for _ in Municipality.query.all() if _.municipal_id != '1']
#     ids = str(field.data)
#     if not field.data:
#         raise ValidationError(u'هذه الخانة اجبارية وبها أرقام فقط')
#     if not ids.isdigit():
#         raise ValidationError(u'هذه الخانة اجبارية وبها أرقام فقط')
#     if len(str(field.data)) != 5:
#         raise ValidationError(u'المعرف البلدي يتكون من 5 أرقام')
#     if ids in panned_list:
#         raise ValidationError(u'هذا المعرف لبلدية أخرى')
