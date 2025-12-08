from flask import Flask, render_template
from database import db
from models import Card

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mathly.db'
app.config['SECRET_KEY'] = 'dev'

db.init_app(app)

@app.route('/')
def home():
    cards = Card.query.all()
    return render_template('index.html', cards=cards)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)