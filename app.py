from flask import Flask, render_template_string, request, jsonify
from database import db, Quiz, Option

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SECRET_KEY'] = 'dev-key-12345'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    quizzes = Quiz.query.all()
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Quiz Game</title></head>
    <body>
        <h1>Quiz Game</h1>
        <ul>
        {% for quiz in quizzes %}
            <li><a href="/quiz/{{ quiz.id }}">{{ quiz.title }}</a></li>
        {% endfor %}
        </ul>
    </body>
    </html>
    '''
    return render_template_string(html, quizzes=quizzes)

@app.route('/quiz/<int:quiz_id>')
def quiz(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>{{ quiz.title }}</title></head>
    <body>
        <h1>{{ quiz.title }}</h1>
        <p>Difficulty: {{ quiz.difficulty }}</p>
        <h2>{{ quiz.question }}</h2>
        <form action="/submit" method="POST">
            <input type="hidden" name="quiz_id" value="{{ quiz.id }}">
            {% for option in quiz.options %}
                <button type="submit" name="option_id" value="{{ option.id }}">{{ option.text }}</button>
            {% endfor %}
        </form>
    </body>
    </html>
    '''
    return render_template_string(html, quiz=quiz_obj)

@app.route('/submit', methods=['POST'])
def submit():
    quiz_id = request.form.get('quiz_id', type=int)
    option_id = request.form.get('option_id', type=int)
    
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    option = Option.query.get_or_404(option_id)
    
    if option.quiz_id != quiz_id:
        return jsonify({'error': 'Invalid option for this quiz'}), 400
    
    is_correct = option.is_correct
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head><title>Result</title></head>
    <body>
        <h1>{"Correct!" if is_correct else "Wrong!"}</h1>
        <p>You selected: {option.text}</p>
        <p>Correct answer: {next((o.text for o in quiz_obj.options if o.is_correct), 'N/A')}</p>
        <a href="/">Back to quizzes</a>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    app.run(debug=True)