import random
import math
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

SECTION_CONFIG = {
    'addition': {'operation': '+', 'base_exp': 5, 'color': '#2ecc71'},
    'subtraction': {'operation': '-', 'base_exp': 5, 'color': '#3498db'},
    'multiplication': {'operation': '*', 'base_exp': 7, 'color': '#9b59b6'},
    'division': {'operation': '/', 'base_exp': 7, 'color': '#e67e22'},
    'fractions': {'operation': 'frac', 'base_exp': 8, 'color': '#e74c3c'},
    'mixed': {'operation': 'mix', 'base_exp': 10, 'color': '#1abc9c'},
    'decimals': {'operation': 'dec', 'base_exp': 8, 'color': '#f39c12'},
    'find_value': {'operation': 'solve', 'base_exp': 12, 'color': '#8e44ad'},
}

BASE_UPGRADE_COST = 50


def get_difficulty_params(level):
    """Get min/max numbers based on level. Scales infinitely."""
    if level <= 3:
        min_num = 1
        max_num = 5 + (level * 3)
    elif level <= 6:
        min_num = 1 + (level - 3) * 2
        max_num = 15 + (level - 3) * 10
    elif level <= 10:
        min_num = 5 + (level - 6) * 5
        max_num = 50 + (level - 6) * 25
    else:
        min_num = 10 + (level - 10) * 10
        max_num = 100 + (level - 10) * 50
    return min_num, max_num


def get_exp_reward(section, level):
    """Get XP reward for a correct answer at given level. +1 per level."""
    base = SECTION_CONFIG.get(section, {}).get('base_exp', 5)
    return max(1, base + (level - 1) - 3)


def get_upgrade_cost(current_level):
    """Get cost to upgrade from current_level to current_level + 1. Uses sqrt scaling."""
    return int(BASE_UPGRADE_COST * math.sqrt(current_level))


def get_difficulty_name(level):
    """Get a difficulty label for display."""
    if level <= 2:
        return 'Beginner'
    elif level <= 4:
        return 'Easy'
    elif level <= 6:
        return 'Medium'
    elif level <= 8:
        return 'Hard'
    elif level <= 10:
        return 'Expert'
    else:
        return f'Master {level - 10}'


def generate_problem(section, level):
    """Generate a random math problem for a section at a given level."""
    config = SECTION_CONFIG.get(section, SECTION_CONFIG['addition'])
    op = config['operation']
    min_num, max_num = get_difficulty_params(level)
    exp_reward = get_exp_reward(section, level)

    a = random.randint(min_num, max_num)
    b = random.randint(min_num, max_num)

    if op == '+':
        correct = a + b
        question = f"{a} + {b}"
    elif op == '-':
        if a < b:
            a, b = b, a
        correct = a - b
        question = f"{a} - {b}"
    elif op == '*':
        if level <= 4:
            a = random.randint(1, min(12, max_num))
            b = random.randint(1, min(12, max_num))
        correct = a * b
        question = f"{a} x {b}"
    elif op == '/':
        b = random.randint(max(1, min_num), min(12, max_num))
        correct = random.randint(1, max(1, max_num // b))
        a = correct * b
        question = f"{a} / {b}"
    else:
        correct = a + b
        question = f"{a} + {b}"

    wrong_answers = set()
    spread = max(5, level * 2)
    while len(wrong_answers) < 3:
        offset = random.randint(-spread, spread)
        if offset == 0:
            offset = random.choice([-1, 1])
        wrong = correct + offset
        if wrong != correct and wrong >= 0:
            wrong_answers.add(wrong)

    options = list(wrong_answers) + [correct]
    random.shuffle(options)

    return {
        'question': question,
        'correct': correct,
        'options': options,
        'section': section,
        'level': level,
        'exp_reward': exp_reward
    }


class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    quizzes = db.relationship('Quiz', backref='unit', lazy=True)


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))
    title = db.Column(db.String(255), nullable=False)
    question = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), default='normal')
    options = db.relationship('Option', backref='quiz', lazy=True, cascade='all, delete-orphan')


class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    exp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    is_admin = db.Column(db.Boolean, default=False)

    sector_progress = db.relationship('UserSectorProgress', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_sector_level(self, section):
        """Get user's level in a specific sector."""
        for p in self.sector_progress:
            if p.section == section:
                return p.level
        return 1


class UserSectorProgress(db.Model):
    __tablename__ = 'user_sector_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    section = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, default=1)
    total_problems_solved = db.Column(db.Integer, default=0)
    total_exp_earned = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint('user_id', 'section', name='_user_section_uc'),)


# Keep old models for migration compatibility but they won't be used
class ProblemCategory(db.Model):
    __tablename__ = 'problem_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(50), nullable=False, default='addition')
    level_order = db.Column(db.Integer, default=1)
    operation = db.Column(db.String(10), nullable=False)
    difficulty = db.Column(db.String(50), default='beginner')
    exp_reward = db.Column(db.Integer, default=10)
    min_num = db.Column(db.Integer, default=1)
    max_num = db.Column(db.Integer, default=10)
    cost = db.Column(db.Integer, default=0)
    unlocked_by_default = db.Column(db.Boolean, default=True)
    problems_required = db.Column(db.Integer, default=5)


class UserLevelProgress(db.Model):
    __tablename__ = 'user_level_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('problem_categories.id'), nullable=False)
    problems_completed = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)


class UserUnlock(db.Model):
    __tablename__ = 'user_unlocks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('problem_categories.id'), nullable=False)
