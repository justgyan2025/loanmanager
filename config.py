import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'postgresql://shiv:postgresshiv@localhost/loan_manager'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 