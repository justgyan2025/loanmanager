from app import app, db
from sqlalchemy import text

def update_borrower_email():
    with app.app_context():
        try:
            # Drop the unique constraint on email
            sql = text("""
                ALTER TABLE borrower 
                DROP CONSTRAINT IF EXISTS borrower_email_key;
            """)
            
            db.session.execute(sql)
            db.session.commit()
            print("Updated borrower email column successfully!")
            
        except Exception as e:
            print(f"Error updating borrower email: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    update_borrower_email() 