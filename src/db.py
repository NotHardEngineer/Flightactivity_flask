from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
session = db.session
migrate = Migrate()


def init_app(app):
    from .models import Flights
    db.init_app(app)
    migrate.init_app(app, db)


def create_db():
    db.drop_all()
    db.create_all()
    session.commit()
