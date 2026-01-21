from functools import wraps
from flask import render_template, request, jsonify, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, login_required, current_user

from app import app
from database import (
    db, Unit, Quiz, Option, User, UserSectorProgress,
    generate_problem, get_upgrade_cost, get_difficulty_name,
    get_exp_reward, get_difficulty_params, SECTION_CONFIG
)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


SECTIONS_DISPLAY = {
    'addition': {'name': 'Addition', 'icon': '+', 'available': True},
    'subtraction': {'name': 'Subtraction', 'icon': '-', 'available': True},
    'multiplication': {'name': 'Multiplication', 'icon': 'x', 'available': True},
    'division': {'name': 'Division', 'icon': '/', 'available': True},
    'fractions': {'name': 'Fractions', 'icon': '%', 'available': False},
    'mixed': {'name': 'Mixed Arithmetic', 'icon': '+-', 'available': False},
    'decimals': {'name': 'Decimals', 'icon': '.', 'available': False},
    'find_value': {'name': 'Find the Value', 'icon': '?', 'available': False},
}


@app.route('/')
def index():
    if current_user.is_authenticated:
        units = Unit.query.all()
        return render_template('index.html', units=units)
    return render_template('index.html')


@app.route('/home')
def home():
    units = Unit.query.all()
    return render_template('index.html', units=units)


@app.route('/unit/<int:unit_id>')
def unit(unit_id):
    unit_obj = Unit.query.get_or_404(unit_id)
    return render_template('unit.html', unit=unit_obj)


@app.route('/quiz/<int:quiz_id>')
def quiz(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    return render_template('quiz.html', quiz=quiz_obj)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=login_input).first()
        if not user:
            user = User.query.filter_by(email=login_input).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))

        flash('Invalid username/email or password')

    return render_template('login.html', mode='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already taken')
            return render_template('login.html', mode='Register')

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('login.html', mode='Register')

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('login.html', mode='Register')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/play')
@login_required
def play():
    user_progress = {p.section: p for p in current_user.sector_progress}

    sectors_data = []
    for section_key, display in SECTIONS_DISPLAY.items():
        config = SECTION_CONFIG.get(section_key, {})
        progress = user_progress.get(section_key)

        current_level = progress.level if progress else 1
        total_solved = progress.total_problems_solved if progress else 0
        total_exp = progress.total_exp_earned if progress else 0

        upgrade_cost = get_upgrade_cost(current_level)
        can_upgrade = current_user.exp >= upgrade_cost
        difficulty = get_difficulty_name(current_level)
        exp_per_problem = get_exp_reward(section_key, current_level)
        min_num, max_num = get_difficulty_params(current_level)

        sectors_data.append({
            'key': section_key,
            'name': display['name'],
            'icon': display['icon'],
            'color': config.get('color', '#888'),
            'available': display['available'],
            'level': current_level,
            'difficulty': difficulty,
            'upgrade_cost': upgrade_cost,
            'can_upgrade': can_upgrade,
            'exp_per_problem': exp_per_problem,
            'total_solved': total_solved,
            'total_exp': total_exp,
            'range': f"{min_num}-{max_num}"
        })

    return render_template('play.html', sectors=sectors_data)


@app.route('/play/<section>')
@app.route('/play/<section>/<int:level>')
@login_required
def play_section(section, level=None):
    if section not in SECTION_CONFIG:
        flash('Invalid sector!')
        return redirect(url_for('play'))

    display = SECTIONS_DISPLAY.get(section, {})
    if not display.get('available', False):
        flash('This sector is not available yet!')
        return redirect(url_for('play'))

    max_level = current_user.get_sector_level(section)

    if level is None:
        level = max_level
    elif level < 1 or level > max_level:
        flash('Invalid level!')
        return redirect(url_for('play'))

    force_new = request.args.get('new') == '1'
    quiz_session = session.get('quiz_session')

    if force_new or not quiz_session or quiz_session.get('section') != section or quiz_session.get('level') != level or quiz_session.get('completed') or quiz_session.get('lives', 0) <= 0:
        session['quiz_session'] = {
            'section': section,
            'level': level,
            'current_problem': 1,
            'total_problems': 7,
            'lives': 3,
            'accumulated_exp': 0,
            'completed': False
        }

    problem = generate_problem(section, level)
    session['current_problem'] = problem

    difficulty = get_difficulty_name(level)
    min_num, max_num = get_difficulty_params(level)

    return render_template('problem.html',
                         problem=problem,
                         section=section,
                         section_name=display.get('name', section.title()),
                         user_level=level,
                         difficulty=difficulty,
                         range_display=f"{min_num}-{max_num}",
                         quiz_session=session['quiz_session'])


@app.route('/check_answer', methods=['POST'])
@login_required
def check_answer():
    data = request.get_json()
    user_answer = data.get('answer')

    problem = session.get('current_problem')
    quiz_session = session.get('quiz_session')

    if not problem:
        return jsonify({'error': 'No active problem'}), 400

    if not quiz_session:
        return jsonify({'error': 'No active quiz session'}), 400

    is_correct = int(user_answer) == problem['correct']
    section = problem['section']

    progress = UserSectorProgress.query.filter_by(
        user_id=current_user.id,
        section=section
    ).first()

    if not progress:
        progress = UserSectorProgress(
            user_id=current_user.id,
            section=section,
            level=1,
            total_problems_solved=0,
            total_exp_earned=0
        )
        db.session.add(progress)

    session_complete = False
    session_failed = False
    exp_gained = 0
    total_exp_awarded = 0

    if is_correct:
        quiz_session['accumulated_exp'] += problem['exp_reward']

        if quiz_session['current_problem'] >= quiz_session['total_problems']:
            session_complete = True
            quiz_session['completed'] = True
            total_exp_awarded = quiz_session['accumulated_exp']
            current_user.exp += total_exp_awarded
            progress.total_problems_solved += quiz_session['total_problems']
            progress.total_exp_earned += total_exp_awarded
            db.session.commit()
        else:
            quiz_session['current_problem'] += 1
    else:
        quiz_session['lives'] -= 1
        if quiz_session['lives'] <= 0:
            session_failed = True

    session['quiz_session'] = quiz_session
    session.pop('current_problem', None)

    return jsonify({
        'correct': is_correct,
        'expected': problem['correct'],
        'exp_gained': problem['exp_reward'] if is_correct else 0,
        'total_exp': current_user.exp,
        'total_solved': progress.total_problems_solved,
        'section': section,
        'current_problem': quiz_session['current_problem'],
        'total_problems': quiz_session['total_problems'],
        'lives': quiz_session['lives'],
        'session_complete': session_complete,
        'session_failed': session_failed,
        'total_exp_awarded': total_exp_awarded
    })


@app.route('/upgrade/<section>', methods=['POST'])
@login_required
def upgrade_section(section):
    if section not in SECTION_CONFIG:
        return jsonify({'error': 'Invalid sector'}), 400

    progress = UserSectorProgress.query.filter_by(
        user_id=current_user.id,
        section=section
    ).first()

    if not progress:
        progress = UserSectorProgress(
            user_id=current_user.id,
            section=section,
            level=1,
            total_problems_solved=0,
            total_exp_earned=0
        )
        db.session.add(progress)
        db.session.commit()

    current_level = progress.level
    upgrade_cost = get_upgrade_cost(current_level)

    if current_user.exp < upgrade_cost:
        return jsonify({'error': 'Not enough EXP'}), 400

    current_user.exp -= upgrade_cost
    progress.level += 1
    db.session.commit()

    new_level = progress.level
    new_cost = get_upgrade_cost(new_level)
    new_difficulty = get_difficulty_name(new_level)
    new_exp_reward = get_exp_reward(section, new_level)
    min_num, max_num = get_difficulty_params(new_level)

    return jsonify({
        'success': True,
        'new_level': new_level,
        'remaining_exp': current_user.exp,
        'next_upgrade_cost': new_cost,
        'can_upgrade': current_user.exp >= new_cost,
        'difficulty': new_difficulty,
        'exp_per_problem': new_exp_reward,
        'range': f"{min_num}-{max_num}"
    })


@app.route('/skills')
@login_required
def skills():
    user_progress = {p.section: p for p in current_user.sector_progress}

    skills_data = []
    total_problems = 0
    total_exp_earned = 0

    for section_key, display in SECTIONS_DISPLAY.items():
        config = SECTION_CONFIG.get(section_key, {})
        progress = user_progress.get(section_key)

        current_level = progress.level if progress else 1
        solved = progress.total_problems_solved if progress else 0
        exp_earned = progress.total_exp_earned if progress else 0

        total_problems += solved
        total_exp_earned += exp_earned

        skills_data.append({
            'key': section_key,
            'name': display['name'],
            'icon': display['icon'],
            'color': config.get('color', '#888'),
            'level': current_level,
            'difficulty': get_difficulty_name(current_level),
            'total_solved': solved,
            'total_exp': exp_earned
        })

    return render_template('skills.html',
                         skills=skills_data,
                         total_exp=current_user.exp,
                         total_problems=total_problems,
                         total_exp_earned=total_exp_earned)


@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.query.order_by(User.exp.desc()).all()
    return render_template('admin.html', users=users)


@app.route('/admin/modify_exp', methods=['POST'])
@login_required
@admin_required
def admin_modify_exp():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount', 0)
    action = data.get('action')

    if not user_id or not action:
        return jsonify({'error': 'Missing parameters'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400

    if action == 'add':
        user.exp += amount
    elif action == 'deduct':
        user.exp = max(0, user.exp - amount)
    elif action == 'set':
        user.exp = max(0, amount)
    else:
        return jsonify({'error': 'Invalid action'}), 400

    db.session.commit()

    return jsonify({
        'success': True,
        'user_id': user.id,
        'username': user.username,
        'new_exp': user.exp
    })


@app.route('/admin/set_level', methods=['POST'])
@login_required
@admin_required
def admin_set_level():
    data = request.get_json()
    user_id = data.get('user_id')
    section = data.get('section')
    level = data.get('level')

    if not user_id or not section or level is None:
        return jsonify({'error': 'Missing parameters'}), 400

    if section not in SECTION_CONFIG:
        return jsonify({'error': 'Invalid section'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        level = max(1, int(level))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid level'}), 400

    progress = UserSectorProgress.query.filter_by(
        user_id=user_id,
        section=section
    ).first()

    if not progress:
        progress = UserSectorProgress(
            user_id=user_id,
            section=section,
            level=level,
            total_problems_solved=0,
            total_exp_earned=0
        )
        db.session.add(progress)
    else:
        progress.level = level

    db.session.commit()

    return jsonify({
        'success': True,
        'user_id': user.id,
        'section': section,
        'new_level': level
    })
