import logging
from schoolbloc import db
from datetime import datetime

log = logging.getLogger(__name__)


class ScheduleError(Exception):
    pass


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

    def __init__(self):
        self.created_at = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()
        log.info('added new schedule')

    def __repr__(self):
        return "<id={}>".format(self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
