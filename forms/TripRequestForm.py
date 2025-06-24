from wtforms import SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, HiddenField, SubmitField


vehicle_type = SelectField("Tipo de vehículo", choices=[
    ('auto', 'Auto'),
    ('moto', 'Moto')
], validators=[DataRequired()])
payment_method = SelectField("Forma de pago", coerce=int, validators=[DataRequired()])
