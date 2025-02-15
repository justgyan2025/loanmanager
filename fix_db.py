from app import app, db
from models import Admin, Borrower, Loan, Payment
from werkzeug.security import generate_password_hash
from sqlalchemy import text
import time

def fix_database():
    with app.app_context():
        try:
            print("Starting database repair...")
            
            # Test connection
            db.session.execute(text('SELECT 1'))
            print("Database connection successful!")
            
            # Create tables if they don't exist
            print("Ensuring tables exist...")
            db.create_all()
            
            # Check admin user
            admin = Admin.query.first()
            if not admin:
                print("Creating admin user...")
                admin = Admin(
                    username='admin',
                    password=generate_password_hash('admin123')
                )
                db.session.add(admin)
                db.session.commit()
            
            # Verify tables
            tables = ['admin', 'borrower', 'loan', 'payment']
            for table in tables:
                count = db.session.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                ).scalar()
                print(f"{table}: {count} rows")
            
            print("Database repair completed!")
            return True
            
        except Exception as e:
            print(f"Error during repair: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    fix_database() 