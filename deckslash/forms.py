from wtforms import Form, fields
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(Form):
    username = fields.StringField('Username',
                           [DataRequired(), Length(min=2, max=20)])
    email = fields.StringField('Email',
                        [DataRequired(), Email()])
    password = fields.PasswordField('Password', [DataRequired()])
    confirm_password = fields.PasswordField('Confirm Password',
                                     [DataRequired(), EqualTo('password')])


class LoginForm(Form):
    email = fields.StringField('Email',
                        validators=[DataRequired(), Email()])
    password = fields.PasswordField('Password', validators=[DataRequired()])
