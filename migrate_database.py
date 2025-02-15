from app import app, db
from models import Admin, Borrower, Loan, Payment
from werkzeug.security import generate_password_hash
from sqlalchemy import text
import time

def migrate_database():
    with app.app_context():
        try:
            print("Starting database migration...")
            
            # Drop existing tables if they exist
            print("Dropping existing tables...")
            db.drop_all()
            
            # Create new tables
            print("Creating new tables...")
            db.create_all()
            
            # Create admin user
            print("Creating admin user...")
            admin = Admin(
                username='admin',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            
            # Commit changes
            print("Committing changes...")
            db.session.commit()
            
            # Verify tables
            tables = ['admin', 'borrower', 'loan', 'payment']
            print("\nVerifying table structure:")
            for table in tables:
                result = db.session.execute(
                    text(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = :table
                        ORDER BY ordinal_position
                    """),
                    {'table': table}
                )
                print(f"\n{table.upper()} table:")
                print("-" * 60)
                print(f"{'Column':<20} {'Type':<15} {'Nullable':<10}")
                print("-" * 60)
                for row in result:
                    print(f"{row[0]:<20} {row[1]:<15} {row[2]:<10}")
            
            print("\nMigration completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    try:
        migrate_database()
    except KeyboardInterrupt:
        print("\nMigration cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}") 