import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db  # Import app and db from app.py
from werkzeug.security import generate_password_hash
from sqlalchemy import text
import time
from models import Admin, Borrower, Loan, Payment

def reset_database():
    with app.app_context():
        try:
            # Drop all existing connections
            db.session.execute(text("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = current_database()
                AND pid <> pg_backend_pid();
            """))
            db.session.commit()
            
            # Drop all tables
            print("Dropping all tables...")
            db.drop_all()
            
            # Create all tables
            print("Creating all tables...")
            db.create_all()
            
            # Create admin user
            print("Creating admin user...")
            admin = Admin(
                username='admin',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            
            # Verify the borrower table structure
            sql = text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'borrower'")
            result = db.session.execute(sql)
            print("\nBorrower table columns:")
            for row in result:
                print(f"- {row[0]}: {row[1]}")
            
            print("\nDatabase reset completed successfully!")
            
        except Exception as e:
            print(f"Error during database reset: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    reset_database()