from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=255)])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    nombre = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    telefono = StringField("Phone Number", validators=[DataRequired(), Length(min=6, max=15)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=255)])
    role_id = HiddenField()
    submit = SubmitField("Register")
