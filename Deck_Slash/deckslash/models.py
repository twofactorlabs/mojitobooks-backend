from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from deckslash import db, ma, app

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(90), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_image = db.Column(db.String(200), nullable=False,
                              default='default-avatar.png')
    bio = db.Column(db.Text)
    cards = db.relationship('Card', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
        
    def __repr__(self):
        return f"User('{self.name}', '{self.username}', '{self.profile_image}')"

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    picture = db.Column(db.String(20), nullable=False,
                        default='card_default.png')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Card('{self.title}', '{self.date_posted}')"

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        fields = ('username','email','name','profile_image','bio')

class CardSchema(ma.ModelSchema):
    class Meta:
        model = Card
        fields = ('id', 'title', 'description', 'likes', 'date_posted', 'picture', 'author')
