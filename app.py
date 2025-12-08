from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database import db
from models import Card, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mathly.db'
app.config['SECRET_KEY'] = 'change_this_secret_key_later' 

db.init_app(app)

# --- AUTH SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Send unauthorized users here

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
@login_required # <--- THE GATEKEEPER
def home():
    if request.method == 'POST':
        raw_text = request.form.get('user_input')
        # We now attach the card to the CURRENT USER
        new_card = Card(text=raw_text, user_id=current_user.id)
        db.session.add(new_card)
        db.session.commit()

    # Only show cards belonging to THIS user
    my_cards = Card.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', cards=my_cards, user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username taken.')
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template('login.html', mode='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid credentials.')
    return render_template('login.html', mode='Login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)