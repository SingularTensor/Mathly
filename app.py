from flask import Flask, render_template, request
from database import db
from models import Card

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///naked.db'

# Connect the database engine to this app
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        raw_text = request.form.get('user_input')
        new_card = Card(text=raw_text)
        db.session.add(new_card)
        db.session.commit()

    all_cards = Card.query.all()
    return render_template('index.html', cards=all_cards)

if __name__ == '__main__':
    app.run(debug=True)