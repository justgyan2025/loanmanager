import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'postgresql://shiv:bKbEgU8Gs3KdqnaqSwnXfPl3W2fv3dk2@localhost/loanmangerdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False