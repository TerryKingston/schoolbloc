import logging
from schoolbloc import db

log = logging.getLogger(__name__)


class Subject(db.Model):
    """
    ORM object for subjects stored in the database

    A subject is a group of courses
    """
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
