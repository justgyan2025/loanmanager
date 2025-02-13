import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def add_payment_type_column():
    with app.app_context():
        try:
            sql = text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name='payment' AND column_name='payment_type'
                    ) THEN
                        ALTER TABLE payment ADD COLUMN payment_type VARCHAR(20) NOT NULL DEFAULT 'PRINCIPAL';
                    END IF;
                END $$;
            """)
            
            db.session.execute(sql)
            db.session.commit()
            print("Added payment_type column successfully!")
            
        except Exception as e:
            print(f"Error adding payment_type column: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    add_payment_type_column() 