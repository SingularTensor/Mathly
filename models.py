from database import db

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))