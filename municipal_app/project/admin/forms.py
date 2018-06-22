# project/admin/forms.py
# -*- coding: utf-8 -*

from flask_wtf import Form
from wtforms import PasswordField, TextField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from project.models import Municipality


class ChangePwdForm(Form):
    admin_password = PasswordField('password', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
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


def validate_municipal_id(form, field):
    panned_list = [_.municipal_id for _ in Municipality.query.all() if _.municipal_id != '1']
    ids = str(field.data)
    if not field.data:
        raise ValidationError(u'هذه الخانة اجبارية وبها أرقام فقط')
    if not ids.isdigit():
        raise ValidationError(u'هذه الخانة اجبارية وبها أرقام فقط')
    if len(str(field.data)) != 5:
        raise ValidationError(u'المعرف البلدي يتكون من 5 أرقام')
    if ids in panned_list:
        raise ValidationError(u'هذا المعرف لبلدية أخرى')


class AddmunForm(Form):
    municipal_name = TextField('municipal_name', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    municipal_name_ar = TextField('municipal_name_ar', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    municipal_id = TextField('municipal_id', validators=[validate_municipal_id])
    municipal_long = FloatField('municipal_long', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    municipal_lat = FloatField('municipal_lat', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    choices_state = [(None, '')]
    choices_approved = [(None, ''), ('signed', u'وقعت'), ('notsigned', u'غير موقع')]
    choices_state.extend([(_.municipal_state, _.municipal_state) for _ in Municipality.query.all() if _.municipal_id != '1'])
    approved = SelectField('approved', validators=[DataRequired()], choices=choices_approved)
    municipal_state = SelectField('municipal_state', validators=[DataRequired()], choices=sorted(list(set(choices_state))))
