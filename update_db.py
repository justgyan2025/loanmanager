from app import app, db
from sqlalchemy import text

def update_database():
    with app.app_context():
        try:
            # Add monthly_emi column if it doesn't exist
            sql = text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name='loan' AND column_name='monthly_emi'
                    ) THEN
                        ALTER TABLE loan ADD COLUMN monthly_emi FLOAT;
                    END IF;
                END $$;
            """)
            
            db.session.execute(sql)
            db.session.commit()
            print("Database update completed successfully!")
            
            # Verify the column was added
            verify_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name = 'loan'")
            result = db.session.execute(verify_sql)
            columns = [row[0] for row in result]
            print("\nLoan table columns:", columns)
            
        except Exception as e:
            print(f"Error during database update: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    update_database()