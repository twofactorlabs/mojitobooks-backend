from wtforms import Form, fields
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from deckslash.models import User


class RegistrationForm(Form):
    name = fields.StringField('Username',
                           [DataRequired(), Length(min=2, max=90)])
    email = fields.StringField('Email',
                        [DataRequired(), Email()])
    password = fields.PasswordField('Password', [DataRequired()])
    confirm_password = fields.PasswordField('Confirm Password',
                                     [DataRequired(), EqualTo('password')])

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is taken.Please choose a different one')


class LoginForm(Form):
    email = fields.StringField('Email',
                        validators=[DataRequired(), Email()])
    password = fields.PasswordField('Password', validators=[DataRequired()])
