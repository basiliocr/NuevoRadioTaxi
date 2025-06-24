from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange, Optional

class ReviewForm(FlaskForm):
    calificacion = IntegerField("Calificación (1 a 5 estrellas)", validators=[
        InputRequired(), NumberRange(min=1, max=5)
    ])
    comentario = TextAreaField("Comentario", validators=[Optional()])
    submit = SubmitField("Enviar Reseña")
