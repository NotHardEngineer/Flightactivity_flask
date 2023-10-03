from contextlib import contextmanager
import datetime

from sqlalchemy.exc import SQLAlchemyError

from src.db import db


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
    fid = db.Column(db.String, nullable=False, unique=True) # Compilation of number and scheduled date
    number = db.Column(db.String, nullable=False)
    sh_time = db.Column(db.Time, nullable=False)
    sh_date = db.Column(db.Date, nullable=False)
    et_time = db.Column(db.Time, nullable=False)
    et_date = db.Column(db.Date, nullable=False)
    airport_iata = db.Column(db.String(4), nullable=False)
    is_depart = db.Column(db.Boolean, nullable=False)
    vessel_type = db.Column(db.String(255), default='unknown')
    vessel_model = db.Column(db.String(255), default='unknown')
    company = db.Column(db.String(255), default='unknown')

    def __repr__(self):
        return f"<Flight number {self.number}> on {self.sh_date}, by {self.company}"
