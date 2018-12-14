from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import random, string

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits)
                                   for x in range(32))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

from deckslash import rest_api
