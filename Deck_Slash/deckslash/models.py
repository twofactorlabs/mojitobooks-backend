from datetime import datetime
from deckslash import db, ma

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(90), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_image = db.Column(db.String(200), nullable=False,
                              default='default-avatar.png')
    bio = db.Column(db.Text, nullable = False, default='This is my bio')
    cards = db.relationship('Card', backref='author', lazy=True)
        
    def __repr__(self):
        return f"User('{self.name}', '{self.username}', '{self.profile_image}')"

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text)
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
        fields = ('id', 'title', 'description', 'link', 'date_posted', 'picture', 'author')
