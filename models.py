from app import app, db
from database import Quiz, Option

with app.app_context():
    q = Quiz(title="Math Quiz", question="2 + 2 = ?", difficulty="easy")
    q.options = [
        Option(text="3", is_correct=False),
        Option(text="4", is_correct=True),
        Option(text="5", is_correct=False)
    ]
    db.session.add(q)
    db.session.commit()