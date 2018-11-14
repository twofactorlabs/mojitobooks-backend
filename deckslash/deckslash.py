from flask import Flask, request
from flask_restful import Resource, Api
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c24170e00d0368506c875c08b016f5b9'
api = Api(app)

class Home(Resource):
    def get(self):
        dict1 = {'Hello': 'World'}
        return dict1, 201

class About(Resource):
    def get(self):
        return {'about':'Hello, This is an About Page'}, 201

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
api.add_resource(About, '/about')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')

if __name__ == '__main__':
    app.run(debug=True)
