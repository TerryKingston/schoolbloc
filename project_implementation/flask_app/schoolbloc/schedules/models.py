import logging
from schoolbloc import db

log = logging.getLogger(__name__)


class Schedule(db.Model):
    """
    ORM object for schedules stored in the database

    A schedule is the result of the scheduler process. A scheduler
    includes a list of Classes which represent a mapping of teacher,
    students, clasroom, time, and course.
    """
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
