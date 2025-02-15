from app import app, db
from models import Admin, Borrower, Loan, Payment
from werkzeug.security import generate_password_hash
from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError
import ssl
import time

def wait_for_db(max_retries=5, delay=5):
    """Wait for database to be ready"""
    for attempt in range(max_retries):
        try:
            # Test the connection
            with app.app_context():
                db.session.execute(text('SELECT 1'))
                print("Database connection successful!")
                return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries}: Database not ready yet... ({str(e)})")
            if attempt < max_retries - 1:
                time.sleep(delay)
    return False

def migrate_to_render():
    """Migrate database to Render"""
    print("Starting database migration to Render...")
    
    # Wait for database to be ready
    if not wait_for_db():
        print("Could not connect to database after multiple attempts. Aborting.")
        return False

    with app.app_context():
        try:
            # Drop existing tables if they exist
            print("Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            print("Creating new tables...")
            db.create_all()
            
            # Create admin user
            print("Creating admin user...")
            admin = Admin(
                username='admin',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            
            # Verify the database structure
            tables = ['admin', 'borrower', 'loan', 'payment']
            for table in tables:
                try:
                    sql = text(f"""
                        SELECT column_name, data_type, is_nullable 
                        FROM information_schema.columns 
                        WHERE table_name = :table
                        ORDER BY ordinal_position
                    """)
                    result = db.session.execute(sql, {'table': table})
                    print(f"\n{table.capitalize()} table structure:")
                    print("-" * 50)
                    for row in result:
                        nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                        print(f"Column: {row[0]:<20} Type: {row[1]:<15} {nullable}")
                except Exception as e:
                    print(f"Error checking table {table}: {str(e)}")
            
            print("\nDatabase migration completed successfully!")
            return True
            
        except OperationalError as e:
            print(f"Database connection error: {str(e)}")
            print("Please check your database credentials and connection.")
            db.session.rollback()
            return False
            
        except ProgrammingError as e:
            print(f"SQL error: {str(e)}")
            print("There might be an issue with the SQL syntax or database permissions.")
            db.session.rollback()
            return False
            
        except Exception as e:
            print(f"Unexpected error during migration: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    try:
        success = migrate_to_render()
        if success:
            print("\nMigration completed successfully!")
            print("You can now start your application.")
        else:
            print("\nMigration failed. Please check the errors above.")
    except KeyboardInterrupt:
        print("\nMigration cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}") 