from datetime import datetime
from deckslash import db, ma

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_image = db.Column(db.String(20), nullable=False,
                              default='/static/ProfileImage/default-avatar.png')
    bio = db.Column(db.Text, nullable = False, default='This is my bio')
    cards = db.relationship('Card', backref='author', lazy=True)
        
    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.profile_image}')"

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    picture = db.Column(db.String(20), nullable=False,
                        default='/static/CardPicture/card_default.png')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Card('{self.title}', '{self.date_posted}')"

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

class CardSchema(ma.ModelSchema):
    class Meta:
        model = Card
