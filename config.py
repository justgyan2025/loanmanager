import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "123456789")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://shiv:bKbEgU8Gs3KdqnaqSwnXfPl3W2fv3dk2@dpg-cun38m56l47c739b6m0g-a/loanmangerdb")
    SQLALCHEMY_TRACK_MODIFICATIONS = False