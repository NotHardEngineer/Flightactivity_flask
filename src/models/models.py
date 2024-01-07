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
    fid = db.Column(db.String, nullable=False, unique=True)  # Compilation of number and scheduled date
    number = db.Column(db.String, nullable=False)
    sh_time = db.Column(db.Time, nullable=False)
    sh_date = db.Column(db.Date, nullable=False)
    et_time = db.Column(db.Time, nullable=False)
    et_date = db.Column(db.Date, nullable=False)
    airport_iata = db.Column(db.String(4), nullable=False)
    is_depart = db.Column(db.Boolean, nullable=False)
    vessel_type = db.Column(db.String(255), default='unknown')
    vessel_model = db.Column(db.String(255), default='unknown')
    company = db.Column(db.String(255), db.ForeignKey("companies.name"), default='unknown')

    def __repr__(self):
        return f"Flight number {self.number}> on {self.sh_date}, by {self.company}"

    # def update_eta(self, et_date: str, et_time: str):
    #
    #     # Add data validation later
    #
    #     with session_db() as s:
    #


class Companies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    time_create = db.Column(db.DateTime, default=datetime.datetime.now())
    primary_color = db.Column(db.String(6), default="000000")
    secondary_color = db.Column(db.String(6), default="bb33dd")

    def __repr__(self):
        return self.name
