import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_DIR = os.path.join(BASE_DIR, "database")

# Create database directory if it doesn't exist
os.makedirs(DATABASE_DIR, exist_ok=True)


class Config:
    SECRET_KEY = "change-this-secret-key"

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(DATABASE_DIR, "finance.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False