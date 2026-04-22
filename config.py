import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///" + os.path.join(BASE_DIR, "instance", "database.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000").rstrip("/")

    HOST_EMAIL = os.getenv("HOST_EMAIL")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    APP_PASSWORD = os.getenv("APP_PASSWORD")