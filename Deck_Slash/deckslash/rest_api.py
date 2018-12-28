import os
import secrets
from flask import request
from flask_restful import Resource
from deckslash import app, api, db, bcrypt, mail
from deckslash.models import User, Card, UserSchema, CardSchema
from deckslash.forms import (RegistrationForm, LoginForm, UpdateAccountForm, CardForm, PictureForm,
                             RequestResetForm, ResetPasswordForm, set_current_user)
from flask_jwt_extended import jwt_required, create_access_token, jwt_refresh_token_required, create_refresh_token, get_jwt_identity
from flask_mail import Message
import datetime
import uuid
from functools import wraps


# GLOBAL FUNCTIONS
def token_required(f):
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        current_user = User.query.filter_by(public_id=get_jwt_identity()).first()
        return f(current_user, *args, **kwargs)
    return decorated

def save_picture(form_picture, pic_type):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    if pic_type == 'profile':
        picture_path = os.path.join(app.root_path, 'static/ProfileImage', picture_fn)
    elif pic_type == 'card':
        picture_path = os.path.join(app.root_path, 'static/CardPicture', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='mojitobooks@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{'http://localhost:3000/reset_password/' + token}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


# FOR ADMIN AND TESTING ONLY
class TestUser(Resource):
    def get(self):
        user_schema = UserSchema(many=True)
        output = user_schema.dump(User.query.all()).data 
        return output, 200

class TestCard(Resource):
    def get(self):
        card_schema = CardSchema(many=True)
        output = card_schema.dump(Card.query.all()).data 
        return output, 200


# REAL APPLICATION

# Functions for anonymous users
class Search(Resource):
    def get(self):
        card_schema = CardSchema(many=True)
        output = card_schema.dump(Card.query.order_by('date_posted desc').limit(30).all()).data 
        return output, 200
    
    def post(self):
        term = request.get_json()['term']
        card_schema = CardSchema(many=True)
        if term:
            output = card_schema.dump(Card.query.filter(Card.title.contains(term)).order_by('date_posted desc').limit(30).all()).data
            return output, 200
        else:
            output = card_schema.dump(Card.query.order_by('date_posted desc').limit(30).all()).data 
            return output, 200

class Users(Resource):
    def get(self, username):
        user_schema = UserSchema()
        card_schema = CardSchema(many=True)
        user = User.query.filter_by(username=username).first_or_404()
        output = {'user': user_schema.dump(user).data, 'cards': card_schema.dump(user.cards).data}
        return output, 200

# Functions for authorized users
class Profile(Resource):
    @token_required
    def get(current_user, self):
        user_schema = UserSchema()
        card_schema = CardSchema(many=True)
        output = {'user':user_schema.dump(current_user).data, 'cards': card_schema.dump(current_user.cards).data}
        return output, 200

    @token_required
    def post(current_user, self):
        set_current_user(current_user)
        form = UpdateAccountForm(data=request.get_json())
        if form.validate():
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.name = form.name.data
            current_user.bio = form.bio.data
            db.session.commit()
            return {'message': 'Account successfully updated'}, 205
        return form.errors, 400

class ProfilePicture(Resource):
    @token_required
    def post(current_user, self):
        form = PictureForm(data=request.files)
        if form.validate():
            if form.picture.data:
                picture_file = save_picture(form.picture.data[0] if type(form.picture.data) is list else form.picture.data, 'profile')
                if current_user.profile_image != 'default-avatar.png':
                    os.remove(os.path.join(app.root_path, 'static/ProfileImage' ,current_user.profile_image))
                current_user.profile_image = picture_file
                db.session.commit()
                return {'message': 'Profile Picture successfully updated'}, 205
        return form.errors, 400
        
class Post(Resource):
    def get(self, card_id):
        card_schema = CardSchema()
        card = Card.query.filter_by(id=card_id).first_or_404()
        output = card_schema.dump(card).data 
        return output, 200
    
    @token_required
    def post(current_user, self):
        data = request.form
        form_pic = PictureForm(data=request.files)
        form_text = CardForm(data)
        if form_pic.validate() and form_text.validate():
            card = Card(title=data['title'], description=data['description'], user_id=current_user.id)
            if form_pic.picture.data:
                picture_file = save_picture(form_pic.picture.data[0] if type(form_pic.picture.data) is list else form_pic.picture.data, 'card')
                card.picture = picture_file
            db.session.add(card)
            db.session.commit()
            return {'message':'New post created!'}, 201
        return [form_pic.errors, form_text.errors], 400

    @token_required
    def put(current_user, self, card_id):
        form = CardForm(data=request.get_json())
        if form.validate():
            card = Card.query.filter_by(id=card_id).first_or_404()
            if card in current_user.cards:
                card.title = form.title.data
                card.description = form.description.data
                db.session.commit()
                return {'message':'Card successfully updated'}, 205
            else:
                return {'message':'User does not own this card'}, 404
        else:
            return form.errors, 400

    @token_required
    def delete(current_user, self, card_id):
        card = Card.query.filter_by(id=card_id).first_or_404()
        if card in current_user.cards:
            if card.picture != 'card_default.png':
                os.remove(os.path.join(app.root_path, 'static/CardPicture' ,card.picture))
            db.session.delete(card)
            db.session.commit()
            return {'message':'Successfully deleted post!'}, 205
        else:
            return {'message': 'User does not own this card'}, 404
        


# AUTHENTICATION AND AUTHORIZATION
class Login(Resource):
    def post(self):
        form = LoginForm(data=request.get_json())
        if form.validate():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                return {'access_token': create_access_token(identity=user.public_id, expires_delta=datetime.timedelta(days=3)),
                        'refresh_token': create_refresh_token(identity=user.public_id, expires_delta=False)}, 200
            else:
                return {'password':['Wrong password']}, 401
        else:
                return form.errors, 400

class Register(Resource):
    def post(self):
        form = RegistrationForm(data=request.get_json())
        if form.validate():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(public_id=str(uuid.uuid4()) , username = form.username.data, email = form.email.data, name = form.name.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            return {'message':'New user created!'}, 201
        else:
            return form.errors, 400

class Refresh(Resource):
    @jwt_refresh_token_required
    def get(self):
        current_user = User.query.filter_by(public_id=get_jwt_identity()).first()
        return {'access_token': create_access_token(identity=current_user.public_id, expires_delta=datetime.timedelta(days=3))}, 200

class ResetRequest(Resource):
    def post(self):
        form = RequestResetForm(data=request.get_json())
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            send_reset_email(user)
            return {'message': 'An email has been sent with instructions to reset your password.'}, 200
        else:
            return form.errors, 400

class ResetPassword(Resource):
    def post(self, token):
        user = User.verify_reset_token(token)
        if user is None:
            return {'message':'That is an invalid or expired token'}, 401
        form = ResetPasswordForm(data=request.get_json())
        if form.validate():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            return {'message':'Your password has been updated!'}, 200


api.add_resource(TestUser, '/testuser')
api.add_resource(TestCard, '/testcard')
api.add_resource(Search, '/search')
api.add_resource(Users, '/users/<string:username>')
api.add_resource(Profile, '/profile')
api.add_resource(ProfilePicture, '/profilepic')
api.add_resource(Post, '/post', '/post/<int:card_id>')

api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(Refresh, '/refresh')
api.add_resource(ResetRequest, '/reset_password')
api.add_resource(ResetPassword, '/reset_password/<token>')
