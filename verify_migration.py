from app import app, db
from sqlalchemy import text

def verify_migration():
    with app.app_context():
        try:
            print("Verifying database migration...")
            
            # Check database connection
            result = db.session.execute(text('SELECT version()'))
            version = result.scalar()
            print(f"\nPostgreSQL Version: {version}")
            
            # Check table existence and row counts
            tables = ['admin', 'borrower', 'loan', 'payment']
            print("\nTable Status:")
            print("-" * 50)
            print(f"{'Table':<20} {'Row Count':<10} {'Status'}")
            print("-" * 50)
            
            for table in tables:
                try:
                    result = db.session.execute(text(f'SELECT COUNT(*) FROM {table}'))
                    count = result.scalar()
                    print(f"{table:<20} {count:<10} ✓ OK")
                except Exception as e:
                    print(f"{table:<20} {'N/A':<10} ✗ Error: {str(e)}")
            
            # Check admin user
            result = db.session.execute(text('SELECT username FROM admin'))
            admin = result.scalar()
            print(f"\nAdmin user present: {'✓ Yes' if admin else '✗ No'}")
            
            print("\nVerification completed!")
            return True
            
        except Exception as e:
            print(f"Verification error: {str(e)}")
            return False

if __name__ == "__main__":
    verify_migration() 