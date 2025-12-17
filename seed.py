from app import app
from database import db, Quiz, Option

def seed_db():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Add sample quizzes
        q1 = Quiz(title="Math Quiz", question="2 + 2 = ?", difficulty="easy")
        q1.options = [
            Option(text="3", is_correct=False),
            Option(text="4", is_correct=True),
            Option(text="5", is_correct=False)
        ]
        
        q2 = Quiz(title="Capital Cities", question="What is the capital of France?", difficulty="medium")
        q2.options = [
            Option(text="London", is_correct=False),
            Option(text="Paris", is_correct=True),
            Option(text="Berlin", is_correct=False)
        ]
        
        db.session.add(q1)
        db.session.add(q2)
        db.session.commit()
        
        print("✅ Database seeded with sample quizzes!")

if __name__ == "__main__":
    seed_db()