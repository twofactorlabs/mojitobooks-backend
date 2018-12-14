from flask import request
from flask_restful import Resource
from deckslash import app, api, db, bcrypt
from deckslash.models import User, Card, UserSchema, CardSchema
from deckslash.forms import RegistrationForm, LoginForm
from flask_jwt_extended import jwt_required, create_access_token, jwt_refresh_token_required, create_refresh_token, get_jwt_identity
import datetime
import uuid
from functools import wraps

def token_required(f):
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        current_user = User.query.filter_by(public_id=get_jwt_identity()).first()
        return f(current_user, *args, **kwargs)
    return decorated

# This is for admin
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

# This is for real app
class Search(Resource):
    def post(self):
        term = request.get_json()['term']
        card_schema = CardSchema(many=True)
        if term:
            output = card_schema.dump(Card.query.filter(Card.title.contains(term)).all()).data
            return output, 200
        else:
            output = card_schema.dump(Card.query.all()).data 
            return output, 200

class Users(Resource):
    def get(current_user, self, username):
        user_schema = UserSchema()
        card_schema = CardSchema(many=True)
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'message':'No user found!'}, 400
        output = {'user': user_schema.dump(user).data, 'cards': card_schema.dump(user.cards).data}
        return output, 200

    @token_required
    def put(current_user, self, username):
        #Not yet implemented
        return {'message':'The user has been updated'}, 501

class Cards(Resource):
    @token_required
    def post(current_user, self):
        data = request.get_json()
        card = Card(title=data['title'], description=data['description'], link=data['link'], user_id=current_user.id)
        db.session.add(card)
        db.session.commit()
        return {'message':'New card created!'}, 201

class Login(Resource):
    def post(self):
        form = LoginForm(data=request.get_json())
        if form.validate():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                return {'access_token': create_access_token(identity=user.public_id, expires_delta=datetime.timedelta(hours=1)),
                        'refresh_token': create_refresh_token(identity=user.public_id, expires_delta=False)}, 200
            else:
                return {'password':['Wrong password']}, 401
        else:
                return form.errors, 401

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
        return {'access_token': create_access_token(identity=current_user.public_id, expires_delta=datetime.timedelta(hours=1))}, 200

api.add_resource(Search, '/')
api.add_resource(TestUser, '/testuser')
api.add_resource(TestCard, '/testcard')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(Refresh, '/refresh')
api.add_resource(Users, '/users/<username>')
api.add_resource(Cards, '/cards')
