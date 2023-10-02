from contextlib import contextmanager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


@contextmanager
def session_db():
    """Provide a transactional scope around a series of operations."""
    session = db.session()
    try:
        yield session
    except SQLAlchemyError as e:
        session.rollback()
        raise e


class Flights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    sh_time = db.Column(db.Time, nullable=False)
    sh_date = db.Column(db.DateTime, nullable=False)
    et_time = db.Column(db.DateTime, nullable=False)
    et_date = db.Column(db.DateTime, nullable=False)
    airport_iata = db.Column(db.String(4), nullable=False)
    is_depart = db.Column(db.Boolean, nullable=False)
    vessel_type = db.Column(db.String(255))
    vessel_model = db.Column(db.String(255))
    company = db.Column(db.String(255), default='unknown')

    def __repr__(self):
        return f"<Flight number {self.number}> on {self.sh_date}, from {self.company}"
