from app import app, db
from sqlalchemy import text

def update_payment_table():
    with app.app_context():
        try:
            # Add status column if it doesn't exist
            sql1 = text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name='payment' AND column_name='status'
                    ) THEN
                        ALTER TABLE payment ADD COLUMN status VARCHAR(20) DEFAULT 'COMPLETED';
                    END IF;
                END $$;
            """)
            
            # Add notes column if it doesn't exist
            sql2 = text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name='payment' AND column_name='notes'
                    ) THEN
                        ALTER TABLE payment ADD COLUMN notes TEXT;
                    END IF;
                END $$;
            """)
            
            db.session.execute(sql1)
            db.session.execute(sql2)
            db.session.commit()
            print("Payment table updated successfully!")
            
            # Verify the columns were added
            verify_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name = 'payment'")
            result = db.session.execute(verify_sql)
            columns = [row[0] for row in result]
            print("\nPayment table columns:", columns)
            
        except Exception as e:
            print(f"Error updating payment table: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    update_payment_table() 