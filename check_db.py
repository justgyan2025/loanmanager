from app import app, db
from sqlalchemy import text
from models import Loan

with app.app_context():
    # Check table structure
    sql = text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'loan'")
    result = db.session.execute(sql)
    print("\nLoan table structure:")
    for row in result:
        print(f"Column: {row[0]}, Type: {row[1]}")
    
    # Check if monthly_emi column exists
    try:
        sql = text("SELECT monthly_emi FROM loan LIMIT 1")
        result = db.session.execute(sql)
        print("\nmonthly_emi column exists!")
    except Exception as e:
        print("\nError checking monthly_emi column:", str(e))