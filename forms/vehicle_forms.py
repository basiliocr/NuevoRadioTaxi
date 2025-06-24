from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class VehicleForm(FlaskForm):
    matricula = StringField("Matrícula", validators=[DataRequired(), Length(max=20)])
    marca = StringField("Marca", validators=[DataRequired(), Length(max=50)])
    modelo = StringField("Modelo", validators=[DataRequired(), Length(max=50)])
    anio = IntegerField("Año", validators=[DataRequired()])
    color = StringField("Color", validators=[DataRequired(), Length(max=30)])

    vehicle_type = SelectField("Tipo de vehículo", choices=[
        ("auto", "Auto"),
        ("moto", "Moto")
    ], validators=[DataRequired()])

    submit = SubmitField("Guardar")
