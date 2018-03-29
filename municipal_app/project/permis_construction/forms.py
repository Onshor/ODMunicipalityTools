# project/permis_construction/forms.py


from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, FloatField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from project.models import User, Permisconstruct
from list_municipality import municipalitys


class PermisconstructForm(Form):
    zone_municipale = TextField('Zone municipale', validators=[DataRequired(), Length(max=150)])
    address = TextField('address', validators=[DataRequired(), Length(max=150)])
    description = TextField('description', validators=[DataRequired(), Length(max=255)])
    date_attribution = DateField('date attribution', validators=[DataRequired()], format='%Y/%m/%d')
    date_expiration = DateField('date attribution', validators=[DataRequired()], format='%Y/%m/%d')
    longitude = FloatField('Longitude', validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired()])

    """
    def validate(self):
        initial_validation = super(PermisconstructForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True
    """