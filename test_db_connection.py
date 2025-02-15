from app import app, db
from sqlalchemy import text
import time

def test_connection(max_retries=5):
    print("Testing database connection...")
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Try to execute a simple query
                result = db.session.execute(text('SELECT version()'))
                version = result.scalar()
                
                print(f"\nSuccessfully connected to the database!")
                print(f"PostgreSQL version: {version}")
                
                # Test table access
                tables = ['admin', 'borrower', 'loan', 'payment']
                print("\nChecking table access:")
                for table in tables:
                    try:
                        result = db.session.execute(
                            text(f"SELECT COUNT(*) FROM {table}")
                        )
                        count = result.scalar()
                        print(f"✓ {table}: {count} rows")
                    except Exception as e:
                        print(f"✗ {table}: {str(e)}")
                
                return True
                
        except Exception as e:
            print(f"\nAttempt {attempt + 1}/{max_retries} failed:")
            print(f"Error: {str(e)}")
            
            if attempt < max_retries - 1:
                wait_time = 5
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("\nFailed to connect to the database after multiple attempts.")
                print("Please check your database configuration and credentials.")
                return False

if __name__ == "__main__":
    test_connection() 