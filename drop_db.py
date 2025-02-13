from app import app, db
from sqlalchemy import text

def drop_database():
    with app.app_context():
        try:
            # Drop all tables
            print("Dropping all tables...")
            db.drop_all()
            
            # Drop any remaining tables using PostgreSQL specific query
            db.session.execute(text('''
                DO $$ 
                DECLARE 
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
            '''))
            
            db.session.commit()
            print("Database dropped successfully!")
            
        except Exception as e:
            print(f"Error dropping database: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    drop_database() 