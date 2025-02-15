from app import app, db
from sqlalchemy import text
import time
import sys
import psycopg2
from psycopg2 import OperationalError

def get_connection_info():
    """Extract connection info from SQLAlchemy URI"""
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"\nChecking connection to: {uri.split('@')[1]}")  # Only show host info, not credentials
    return uri

def test_raw_connection(uri):
    """Test direct PostgreSQL connection"""
    try:
        conn = psycopg2.connect(uri)
        conn.close()
        print("✓ Raw PostgreSQL connection successful")
        return True
    except OperationalError as e:
        print("✗ Raw PostgreSQL connection failed:")
        print(f"  Error: {str(e)}")
        return False

def check_database_size():
    """Get database size information"""
    try:
        with app.app_context():
            # Get database size
            size_query = text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                       pg_database_size(current_database()) as bytes
            """)
            result = db.session.execute(size_query)
            size_info = result.fetchone()
            print(f"✓ Database size: {size_info[0]}")
            
            # Get table sizes
            table_size_query = text("""
                SELECT 
                    table_name,
                    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as total_size
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC
            """)
            result = db.session.execute(table_size_query)
            print("\nTable sizes:")
            for row in result:
                print(f"  - {row[0]:<20} {row[1]}")
            return True
    except Exception as e:
        print(f"✗ Error getting database size: {str(e)}")
        return False

def check_table_counts():
    """Get row counts for all tables"""
    try:
        with app.app_context():
            tables = ['admin', 'borrower', 'loan', 'payment']
            print("\nTable row counts:")
            for table in tables:
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  - {table:<20} {count} rows")
            return True
    except Exception as e:
        print(f"✗ Error getting table counts: {str(e)}")
        return False

def check_connection_settings():
    """Check database connection settings"""
    try:
        with app.app_context():
            # Check connection settings
            settings_query = text("""
                SELECT 
                    name,
                    setting,
                    unit
                FROM pg_settings
                WHERE category = 'Connection and Authentication'
                ORDER BY name
            """)
            result = db.session.execute(settings_query)
            print("\nConnection settings:")
            for row in result:
                if row[2]:  # if has unit
                    print(f"  - {row[0]:<30} = {row[1]} {row[2]}")
                else:
                    print(f"  - {row[0]:<30} = {row[1]}")
            return True
    except Exception as e:
        print(f"✗ Error checking connection settings: {str(e)}")
        return False

def test_connection(max_retries=5):
    """Main connection test function"""
    print("Starting database connection test...")
    
    # Get connection info
    uri = get_connection_info()
    
    # Test raw connection first
    if not test_raw_connection(uri):
        print("\nFailed to establish basic connection. Please check:")
        print("1. Database credentials")
        print("2. Network connectivity")
        print("3. Database server status")
        print("4. Firewall settings")
        return False
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Basic connection test
                result = db.session.execute(text('SELECT version()'))
                version = result.scalar()
                print(f"\n✓ PostgreSQL version: {version}")
                
                # Run additional checks
                checks = [
                    check_database_size,
                    check_table_counts,
                    check_connection_settings
                ]
                
                all_successful = all(check() for check in checks)
                
                if all_successful:
                    print("\n✅ All connection tests passed successfully!")
                    return True
                else:
                    print("\n⚠️ Some tests failed. Check the details above.")
                    return False
                
        except Exception as e:
            print(f"\nAttempt {attempt + 1}/{max_retries} failed:")
            print(f"Error: {str(e)}")
            
            if attempt < max_retries - 1:
                wait_time = 5
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("\n❌ Failed to connect after multiple attempts.")
                print("Please check your database configuration and credentials.")
                return False

if __name__ == "__main__":
    try:
        if test_connection():
            print("\nDatabase connection is healthy! ✨")
            sys.exit(0)
        else:
            print("\nDatabase connection check failed! ❌")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nConnection test cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during connection test: {str(e)}")
        sys.exit(1) 