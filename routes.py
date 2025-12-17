from flask import render_template, request, jsonify
from app import app
from database import db, Quiz, Option

@app.route('/')
def index():
    quizzes = Quiz.query.all()
    return render_template('index.html', quizzes=quizzes)

@app.route('/quiz/<int:quiz_id>')
def quiz(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    return render_template('quiz.html', quiz=quiz_obj)

@app.route('/submit', methods=['POST'])
def submit():
    quiz_id = request.form.get('quiz_id', type=int)
    option_id = request.form.get('option_id', type=int)
    
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    option = Option.query.get_or_404(option_id)
    
    if option.quiz_id != quiz_id:
        return jsonify({'error': 'Invalid option for this quiz'}), 400
    
    is_correct = option.is_correct
    correct_answer = next((o.text for o in quiz_obj.options if o.is_correct), 'N/A')
    
    return render_template('result.html', 
                         is_correct=is_correct, 
                         selected=option.text,
                         correct=correct_answer)