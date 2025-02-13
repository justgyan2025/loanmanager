from app import app, db
from models import Admin, Borrower, Loan, Payment
from werkzeug.security import generate_password_hash

def reset_database():
    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            print("Dropped all tables")
            
            # Create all tables
            db.create_all()
            print("Created all tables")
            
            # Create admin user
            admin = Admin(
                username='admin',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Created admin user")
            
            print("Database reset completed successfully!")
            
        except Exception as e:
            print(f"Error during database reset: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    reset_database() 