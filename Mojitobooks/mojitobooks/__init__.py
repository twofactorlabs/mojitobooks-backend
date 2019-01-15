import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import random, string
import datetime

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits)
                                   for x in range(32))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=3)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']= os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD']= os.environ.get('EMAIL_PASS')
mail = Mail(app)

from mojitobooks import rest_api
