import os
from dotenv import load_dotenv
from datetime import timedelta


# Load environment variables
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # Fallback if .env is missing
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # PostgreSQL connection URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    