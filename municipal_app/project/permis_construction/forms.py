# project/permis_construction/forms.py
# -*- coding: utf-8 -*

from flask_wtf import Form
from wtforms import TextField, TextAreaField, FloatField, DateField, IntegerField
from wtforms.validators import DataRequired, Length



class PermisencourForm(Form):
    num_demande = TextField(u'رقم المطلب', validators=[Length(max=80)])
    date_depot = DateField(u'تاريخ إيداع المطلب', format='%Y/%m/%d')
    nom_titulaire = TextField(u'صاحب الرخصة', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(max=150)])
    num_cin = TextField(u'رقم بطاقة التعريف أو رقم جواز السفر', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(max=15)])
    address = TextField(u'العنوان', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(max=150)])
    zone_municipale = TextField(u'المنطقة البلدية', validators=[Length(max=80)])
    desc_construct = TextAreaField(u'وصف الأشغال', validators=[Length(max=255)])
    type_construct = TextField(u'العنوان', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(max=25)])
    longitude = FloatField('Longitude', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    latitude = FloatField('Latitude', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    surface = FloatField('surface', validators=[DataRequired(message=u'هذه الخانة اجباريه')])


class PermisrefuseForm(Form):
    date_refuse = DateField('date attribution', validators=[DataRequired(message=u'هذه الخانة اجباريه')], format='%Y/%m/%d')


class PermisupdateForm(Form):
    num_permis = IntegerField(u'عدد قرار رخصة البناء', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    date_attribution = DateField(u'تاريخ اسناد الرخصة', validators=[DataRequired(message=u'هذه الخانة اجباريه')], format='%Y/%m/%d')
    date_expiration = DateField(u'تاريخ انتهاء الصلوحيّة', validators=[DataRequired(message=u'هذه الخانة اجباريه')], format='%Y/%m/%d')
    mont_charge_fix = IntegerField(u'معلوم قار')
    mont_charge_ascend = IntegerField(u'معلوم تصاعدي')
    mont_cloture = IntegerField(u'سياج')
    mont_decision = IntegerField(u'قرار الترخيص')
