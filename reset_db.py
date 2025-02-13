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
            # Terminate all database connections first
            db.session.execute(text("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = current_database()
                AND pid <> pg_backend_pid();
            """))
            db.session.commit()
            
            # Drop all tables
            print("Dropping all tables...")
            db.session.execute(text('DROP TABLE IF EXISTS payment CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS loan CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS borrower CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS admin CASCADE'))
            db.session.commit()
            
            # Wait a moment
            time.sleep(2)
            
            # Create all tables with new schema
            print("Creating all tables...")
            db.create_all()
            db.session.commit()  # Commit after create_all
            
            # Create admin user
            print("Creating admin user...")
            # Check if admin exists first
            existing_admin = Admin.query.filter_by(username='admin').first()
            if not existing_admin:
                admin = Admin(
                    username='admin',
                    password=generate_password_hash('admin123')
                )
                db.session.add(admin)
                db.session.commit()
            else:
                print("Admin user already exists")
            
            # Verify all table structures
            tables = ['admin', 'borrower', 'loan', 'payment']
            for table in tables:
                sql = text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
                result = db.session.execute(sql)
                print(f"\n{table.upper()} table columns:")
                for row in result:
                    print(f"- {row[0]}: {row[1]}")
            
            print("\nDatabase reset completed successfully!")
            
        except Exception as e:
            print(f"Error during database reset: {str(e)}")
            db.session.rollback()
            raise  # Re-raise to see full error trace
        finally:
            db.session.close()  # Ensure session is closed

if __name__ == "__main__":
    reset_database()