from flask import request
from flask_restful import Resource
from deckslash import app, api
from deckslash.models import User, Card, UserSchema, CardSchema
from deckslash.forms import RegistrationForm, LoginForm

class Home(Resource):
    def get(self):
        dict1 = {'Hello': 'World'}
        return dict1, 201
    
class SearchUser(Resource):
    def get(self):
        user_schema = UserSchema()
        output = user_schema.dump(User.query.with_entities(User.name, User.email, User.profile_image, User.bio).first()).data 
        return output, 201

class SearchCard(Resource):
    def get(self):
        card_schema = CardSchema()
        output = [card_schema.dump(card).data for card in
                  Card.query.with_entities(Card.title, Card.description, Card.date_posted, Card.link, Card.picture).all()]
        return output, 201

class Login(Resource):
    def post(self):
        form = LoginForm(data=request.get_json())
        if form.validate():
            return {'LOGIN':'SUCCESS'}
        else:
            return {'LOGIN':'FAILURE'}

class Register(Resource):
    def post(self):
        form = RegistrationForm(data=request.get_json())
        if form.validate():
            return {'REGISTER':'SUCCESS'}
        else:
            return {'REGISTER':'FAILURE'}

api.add_resource(Home, '/')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(SearchUser, '/searchUser')
api.add_resource(SearchCard, '/searchCard')
