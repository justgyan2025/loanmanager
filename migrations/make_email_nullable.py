from app import app, db
from sqlalchemy import text

def make_email_nullable():
    with app.app_context():
        try:
            # Make email column nullable
            sql = text("""
                ALTER TABLE borrower 
                ALTER COLUMN email DROP NOT NULL;
            """)
            
            db.session.execute(sql)
            db.session.commit()
            print("Made email column nullable successfully!")
            
        except Exception as e:
            print(f"Error making email nullable: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    make_email_nullable() 