# project/permis_construction/forms.py
# -*- coding: utf-8 -*

from flask_wtf import Form
from wtforms import TextField, SelectField, FloatField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from project.models import User, Permisconstruct
from list_municipality import municipalitys


class PermisencourForm(Form):
    num_demande = TextField(u'رقم المطلب', validators=[Length(max=80)])
    date_depot = DateField(u'تاريخ إيداع المطلب', validators=[DataRequired()], format='%Y/%m/%d')
    nom_titulaire = TextField(u'صاحب الرخصة', validators=[DataRequired(), Length(max=150)])
    num_cin = TextField(u'رقم بطاقة التعريف أو رقم جواز السفر', validators=[DataRequired(), Length(max=15)])
    address = TextField(u'العنوان', validators=[DataRequired(), Length(max=150)])
    zone_municipale = TextField(u'المنطقة البلدية', validators=[Length(max=80)])
    desc_construct = TextField(u'وصف الأشغال', validators=[Length(max=255)])
    type_construct = TextField(u'العنوان', validators=[DataRequired(), Length(max=25)])
    longitude = FloatField('Longitude', validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired()])


class PermisrefuseForm(Form):
    date_refuse = DateField('date attribution', validators=[DataRequired()], format='%Y/%m/%d')


class PermisupdateForm(Form):
    num_permis = IntegerField(u'عدد قرار رخصة البناء', validators=[DataRequired()])
    date_attribution = DateField(u'تاريخ اسناد الرخصة', validators=[DataRequired()], format='%Y/%m/%d')
    date_expiration = DateField(u'تاريخ انتهاء الصلوحيّة', validators=[DataRequired()], format='%Y/%m/%d')
    mont_charge_fix = IntegerField(u'معلوم قار')
    mont_charge_ascend = IntegerField(u'معلوم تصاعدي')
    mont_cloture = IntegerField(u'سياج')
    mont_decision = IntegerField(u'قرار الترخيص')
