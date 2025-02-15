import os
from datetime import timedelta
from urllib.parse import urlparse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Get database URL from environment or use default
    database_url = os.environ.get('DATABASE_URL') or \
        'postgresql://shiv:G49sKpivIJaEJbenKkpJm9A6FM7HAYiR@dpg-cuoaekqj1k6c7396g120-a.oregon-postgres.render.com/loan_manager_0bal'
    
    # Fix potential "postgres://" issue in the URL
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'max_overflow': 2,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'loan_manager',
            'sslmode': 'require',
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    }
    
    # Add SSL requirement for production
    if not os.environ.get('FLASK_DEBUG'):
        SQLALCHEMY_ENGINE_OPTIONS['connect_args']['sslmode'] = 'require' 