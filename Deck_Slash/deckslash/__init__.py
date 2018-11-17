from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'c24170e00d0368506c875c08b016f5b9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

from deckslash import rest_api
