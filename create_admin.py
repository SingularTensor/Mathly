from sqlalchemy import text
from app import app
from database import db, User

def create_admin():
    with app.app_context():
        # Add is_admin column if it doesn't exist (migration)
        try:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0'))
                conn.commit()
            print("Added is_admin column to users table")
        except Exception:
            pass  # Column already exists

        # Check if admin already exists
        admin = User.query.filter_by(email='admin@gmail.com').first()

        if admin:
            admin.is_admin = True
            admin.set_password('password')
            db.session.commit()
            print(f"Updated existing admin account: {admin.username}")
        else:
            admin = User(
                username='admin',
                email='admin@gmail.com',
                is_admin=True
            )
            admin.set_password('password')
            db.session.add(admin)
            db.session.commit()
            print("Created admin account:")
            print(f"  Email: admin@gmail.com")
            print(f"  Password: password")

        print("\nAdmin account ready!")

if __name__ == "__main__":
    create_admin()
