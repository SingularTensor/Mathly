from app import app
from database import db
from models import Card

def reset_db():
    with app.app_context():
        db.create_all()
        
        print("✅ Database initialized. No cards added (Tabula Rasa).")

if __name__ == "__main__":
    reset_db()