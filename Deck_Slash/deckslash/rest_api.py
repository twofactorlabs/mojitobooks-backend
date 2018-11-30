from flask import request
from flask_restful import Resource
from deckslash import app, api, db, bcrypt
from deckslash.models import User, Card, UserSchema, CardSchema
from deckslash.forms import RegistrationForm, LoginForm
import uuid
import jwt
import datetime 
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return {'message':'Token is missing!'}, 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return {'message':'Token is invalid!'}, 401
        return f(current_user, *args, **kwargs)
    return decorated

# This is for admin
class TestUser(Resource):
    def get(self):
        user_schema = UserSchema(many=True)
        output = user_schema.dump(User.query.all()).data 
        return output, 201

class TestCard(Resource):
    def get(self):
        card_schema = CardSchema(many=True)
        output = card_schema.dump(Card.query.with_entities(Card.title, Card.description, Card.date_posted, Card.link, Card.picture).all()).data 
        return output, 201

# This is for real app
class Search(Resource):
    @token_required
    def post(self):
        term = request.get_json()['term']
        card_schema = CardSchema(many=True)
        if term:
            output = card_schema.dump(Card.query.with_entities(Card.title, Card.description, Card.date_posted, Card.link, Card.picture).filter(Card.title.contains(term)).all()).data
            return output, 201
        else:
            output = card_schema.dump(Card.query.with_entities(Card.title, Card.description, Card.date_posted, Card.link, Card.picture).all()).data 
            return output, 201

class Profile(Resource):
    @token_required
    def get(current_user, self, username):
        card_schema = CardSchema(many=True)
        user_schema = UserSchema()
        output = {'user': user_schema.dump(current_user).data, 'cards': card_schema.dump(current_user.cards).data}
        return output, 201

    @token_required
    def put(current_user, self, username):
        #Not yet implemented
        return {'message':'The user has been updated'}

class Users(Resource):
    @token_required
    def get(current_user, self, username):
        user_schema = UserSchema()
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'message':'No user found!'}
        output = {'user': user_schema.dump(user).data, 'cards': card_schema.dump(user.cards).data}
        return output, 201

class Cards(Resource):
    @token_required
    def post(current_user, self):
        print(current_user.id)
        data = request.get_json()
        card = Card(title=data['title'], description=data['description'], link=data['link'], user_id=current_user.id)
        db.session.add(card)
        db.session.commit()
        return {'message':'New card created'}, 201

class Login(Resource):
    def post(self):
        form = LoginForm(data=request.get_json())
        if form.validate():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
                return {'token': token.decode('UTF-8')}
            else:
                return {'message':'Could not verify'}, 401
        else:
                return {'message':'Could not verify'}, 401

class Register(Resource):
    def post(self):
        form = RegistrationForm(data=request.get_json())
        if form.validate():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(public_id=str(uuid.uuid4()) , username = form.username.data, name = form.name.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            return {'message':'New user created!'}, 201
        else:
            return {'message':'form validation wrong'}, 401

api.add_resource(Search, '/')
api.add_resource(TestUser, '/testuser')
api.add_resource(TestCard, '/testcard')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(Users, '/users/<username>')
api.add_resource(Profile, '/<username>')
api.add_resource(Cards, '/cards')
