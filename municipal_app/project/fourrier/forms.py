# project/fourrier/forms.py
# -*- coding: utf-8 -*

from flask_wtf import Form
from wtforms import TextField, SelectField, FloatField, DateField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length


class FourrierForm(Form):
    Name_Fourrier = TextField(u'إسم مستودع الحجز', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(max=25)])
    Address_Fourrier = TextField(u'"عنوان  مستودع الحجز "', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(max=150)])
    Longitude = FloatField('Longitude', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    Laltitude = FloatField('Laltitude', validators=[DataRequired(message=u'هذه الخانة اجباريه')])


class DetentionForm(Form):
    choices_auth = [(None, ''), (u'الشرطة البيئية', u'الشرطة البيئية'), (u'الشرطة البلدية', u'الشرطة البلدية'), (u'البلدية', u'البلدية'), (u'شرطة المرور', u'شرطة المرور'), (u'الحرس الوطني', u'الحرس الوطني'), (u'عدل منفذ', u'عدل منفذ'), (u' حرس المرور', u' حرس المرور')]
    Date_Detention = DateField(u'تاريخ الحجز', validators=[DataRequired(message=u'هذه الخانة اجباريه')], format='%Y/%m/%d')
    Cause_Detention = TextField(u'أسباب الحجز', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(max=150)])
    Descr_Detention = TextAreaField(u'وصف المحجوز', validators=[Length(max=250)])
    Name_Owner = TextField(u'اسم واللقب صاحب المحجوز إن وجد', validators=[Length(max=80)])
    Authority_Detention = SelectField(u'أسباب الحجز', validators=[DataRequired(message=u'هذه الخانة اجباريه')], choices=choices_auth)
    Type_Detention = TextField(u'نوع المحجوز', validators=[DataRequired(message=u'هذه الخانة اجباريه'), Length(max=25)])
    Name_Fourrier2 = SelectField(validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    Registration_Detention = TextField(u'الترقيم المنجمي', validators=[Length(max=80)])


class ReleaseForm(Form):
    Num_Bon = TextField(u'عدد الوصل')
    montant_sortie = IntegerField('', validators=[DataRequired(message=u'هذه الخانة اجباريه')])
    Date_Release = DateField(u'تاريخ إسترجاع المحجوز', validators=[DataRequired(message=u'هذه الخانة اجباريه')], format='%Y/%m/%d')
    Note = TextAreaField(u'ملاحظات', validators=[Length(max=250)])