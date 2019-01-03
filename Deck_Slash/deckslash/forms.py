from flask_wtf.file import FileField, FileAllowed
from wtforms import Form, fields
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from deckslash.models import User


currentUser = User.query.first()
def set_current_user(current_user):
    global currentUser
    currentUser = current_user


class RegistrationForm(Form):
    name = fields.StringField('Name',
                           [DataRequired(), Length(min=2, max=90)])
    username = fields.StringField('Username',
                        [DataRequired(), Length(min=2, max=20)])
    email = fields.StringField('Email', [DataRequired(), Email()])
    password = fields.PasswordField('Password', [DataRequired(), Length(min=6)])
    confirm_password = fields.PasswordField('Confirm Password',
                                     [DataRequired(), Length(min=6), EqualTo('password')])

    def validate_username(self, username):
        if username.data.lower() in ['null', 'undefined']:
            raise ValidationError('That username is invalid. Please choose a different one')
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is already used. Please choose a different one')


class LoginForm(Form):
    username = fields.StringField('Username',
                        validators=[DataRequired(), Length(min=2, max=20)])
    password = fields.PasswordField('Password', validators=[DataRequired()])


class UpdateAccountForm(Form):
    name = fields.StringField('Name',
                           [DataRequired(), Length(min=2, max=90)])
    username = fields.StringField('Username',
                        [DataRequired(), Length(min=2, max=20)])
    email = fields.StringField('Email', [DataRequired(), Email()])
    bio = fields.StringField('Bio')

    def validate_username(self, username):
        global currentUser
        if username.data != currentUser.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        global currentUser
        if email.data != currentUser.email:
            email = User.query.filter_by(email = email.data).first()
            if email:
                raise ValidationError('That email is already used. Please choose a different one')

class CardForm(Form):
    title = fields.StringField('Title', [DataRequired(), Length(min=2, max=100)])
    description = fields.StringField('Description', [DataRequired()])
    

class PictureForm(Form):
    picture = FileField('Update Profile Picture', [FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])

class RequestResetForm(Form):
    email = fields.StringField('Email', [DataRequired(), Email()])

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(Form):
    password = fields.PasswordField('Password', [DataRequired(), Length(min=6)])
    confirm_password = fields.PasswordField('Confirm Password',
                                     [DataRequired(), Length(min=6), EqualTo('password')])
    
    
