from wtforms import Form, fields
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from deckslash.models import User


class RegistrationForm(Form):
    name = fields.StringField('Name',
                           [DataRequired(), Length(min=2, max=90)])
    username = fields.StringField('Username',
                        [DataRequired(), Length(min=2, max=20)])
    password = fields.PasswordField('Password', [DataRequired()])
    confirm_password = fields.PasswordField('Confirm Password',
                                     [DataRequired(), EqualTo('password')])

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken.Please choose a different one')


class LoginForm(Form):
    username = fields.StringField('Username',
                        validators=[DataRequired(), Length(min=2, max=20)])
    password = fields.PasswordField('Password', validators=[DataRequired()])
