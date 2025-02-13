from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models after db initialization
from models import Admin, Borrower, Loan, Payment

if __name__ == '__main__':
    with app.app_context():
        # Initialize migration commands
        pass 