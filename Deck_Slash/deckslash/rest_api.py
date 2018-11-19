from flask import request
from flask_restful import Resource
from deckslash import api, db, bcrypt
from deckslash.models import User, Card, UserSchema, CardSchema
from deckslash.forms import RegistrationForm, LoginForm

class UserQuery(Resource):
    def get(self):
        user_schema = UserSchema(many=True)
        output = user_schema.dump(User.query.with_entities(User.name, User.email, User.profile_image, User.bio).all()).data 
        return output, 201

class CardQuery(Resource):
    def get(self):
        card_schema = CardSchema(many=True)
        output = card_schema.dump(Card.query.with_entities(Card.title, Card.description, Card.date_posted, Card.link, Card.picture).all()).data 
        return output, 201

    def post(self):
        term = request.get_json()['term']
        if term:
            return {'result':'not yet implemented'}
        else:
            card_schema = CardSchema(many=True)
            output = card_schema.dump(Card.query.with_entities(Card.title, Card.description, Card.date_posted, Card.link, Card.picture).all()).data 
            return output, 201

class Login(Resource):
    def post(self):
        form = LoginForm(data=request.get_json())
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                return {'message':'success'}
            else:
                return {'error':'failure'}
        else:
                return {'error':'failure'}

class Register(Resource):
    def post(self):
        form = RegistrationForm(data=request.get_json())
        if form.validate():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(email = form.email.data, name = form.name.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            return {'message':'success'}
        else:
            return {'error':'failed'}

api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(UserQuery, '/user')
api.add_resource(CardQuery, '/card')
