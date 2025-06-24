from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField
from wtforms.validators import DataRequired, Length

class TripRequestForm(FlaskForm):
    pickup_address = StringField("Dirección de recogida", validators=[DataRequired(), Length(min=3)])
    dropoff_address = StringField("Dirección de destino", validators=[DataRequired(), Length(min=3)])
    
    vehicle_type = SelectField("Tipo de vehículo", choices=[("auto", "Auto"), ("moto", "Moto")], validators=[DataRequired()])
    payment_method = SelectField("Forma de pago", coerce=int, validators=[DataRequired()])  # 👈 Esta línea faltaba

    pickup_lat = HiddenField()
    pickup_lon = HiddenField()
    dropoff_lat = HiddenField()
    dropoff_lon = HiddenField()
    distancia = HiddenField()
    tarifa_estimada = HiddenField()

    submit = SubmitField("Solicitar viaje")
