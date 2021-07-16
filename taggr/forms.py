from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class SettingsForm(FlaskForm):
    square_api_key = StringField('Square API Key', validators=[DataRequired()])
    dymo_printer_name = SelectField('Dymo Printer Name', validate_choice=False)
