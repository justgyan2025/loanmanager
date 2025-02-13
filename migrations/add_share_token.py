import os
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def add_share_token_column():
    with app.app_context():
        try:
            # Add share_token column if it doesn't exist
            sql = text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name='loan' AND column_name='share_token'
                    ) THEN
                        ALTER TABLE loan ADD COLUMN share_token VARCHAR(32) UNIQUE;
                    END IF;
                END $$;
            """)
            
            db.session.execute(sql)
            db.session.commit()
            print("Added share_token column successfully!")
            
            # Verify the column was added
            verify_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name = 'loan'")
            result = db.session.execute(verify_sql)
            columns = [row[0] for row in result]
            print("\nLoan table columns:", columns)
            
        except Exception as e:
            print(f"Error adding share_token column: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    add_share_token_column() 