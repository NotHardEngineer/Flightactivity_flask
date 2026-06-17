from app import create_app


class Config:
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:pass@db/flightactivity_db"
    SQLALCHEMY_SESSION_OPTIONS = {"expire_on_commit": False}


app = create_app(Config)
