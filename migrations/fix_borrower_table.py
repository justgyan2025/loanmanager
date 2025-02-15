from app import app, db
from sqlalchemy import text

def fix_borrower_table():
    with app.app_context():
        try:
            # Drop email and phone columns if they exist
            sql = text("""
                DO $$ 
                BEGIN 
                    BEGIN
                        ALTER TABLE borrower DROP COLUMN IF EXISTS email;
                        ALTER TABLE borrower DROP COLUMN IF EXISTS phone;
                    EXCEPTION 
                        WHEN undefined_column THEN 
                        NULL;
                    END;
                END $$;
            """)
            
            db.session.execute(sql)
            db.session.commit()
            
            # Verify the table structure
            verify_sql = text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'borrower'")
            result = db.session.execute(verify_sql)
            print("\nBorrower table columns:")
            for row in result:
                print(f"- {row[0]}: {row[1]}")
            
            print("Borrower table fixed successfully!")
            
        except Exception as e:
            print(f"Error fixing borrower table: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    fix_borrower_table() 