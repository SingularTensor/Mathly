from app import app
from database import db, SECTION_CONFIG

def seed_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        print("Database initialized!")
        print(f"Available sectors: {', '.join(SECTION_CONFIG.keys())}")
        print("All problems are now procedurally generated based on user level.")

if __name__ == "__main__":
    seed_db()
