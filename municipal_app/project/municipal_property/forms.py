
# -*- coding: utf-8 -*

from flask_wtf import Form
from wtforms import TextField, SelectField, FloatField
from wtforms.validators import DataRequired, Length


class ProprietyForm(Form):
    choices = [(u'خاص', u'خاص'), (u'عمومي', u'عمومي')]
    Titre_Foncier = TextField(u'Titre_Foncier', validators=[DataRequired(), Length(max=80)])
    Type_du_Bien = TextField(u'Type_du_Bien', validators=[DataRequired(), Length(max=80)])
    Adresse_Localisation = TextField(u'Adresse_Localisation', validators=[DataRequired(), Length(max=250)])
    Mode_Octroi = TextField(u'Mode_Octroi', validators=[DataRequired(), Length(max=80)])
    Surface = FloatField(u'Surface', validators=[DataRequired()])
    Type_Proprety = SelectField(u'Type_Proprety', validators=[DataRequired()], choices=choices)
    Longitude = FloatField('Longitude', validators=[DataRequired()])
    Laltitude = FloatField('Laltitude', validators=[DataRequired()])
    Type_Usage = TextField(u'Type_Usage', validators=[DataRequired()])