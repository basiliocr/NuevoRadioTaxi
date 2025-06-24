from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired

class DriverProfileForm(FlaskForm):
    licencia = StringField("Licencia", validators=[DataRequired(), Length(max=50)])
    fecha_expiracion_licencia = DateField("Fecha de expiración", validators=[DataRequired()])
    ci = StringField("Carnet de Identidad", validators=[DataRequired(), Length(max=20)])

    foto_perfil = FileField("Foto de perfil", validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], "Solo se permiten imágenes JPG o PNG.")
    ])
    documento_seguro = FileField("Documento del seguro (imagen)", validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], "Solo imágenes permitidas.")
    ])

    aceptar_terminos = BooleanField("Acepto los términos y condiciones", validators=[
        DataRequired(message="Debes aceptar los términos para continuar.")
    ])

    submit = SubmitField("Guardar")
