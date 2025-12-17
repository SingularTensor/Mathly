from flask import Flask
from database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SECRET_KEY'] = 'dev-key-12345'

db.init_app(app)

with app.app_context():
    db.create_all()


from routes import *

if __name__ == '__main__':
    app.run(debug=True)