import logging
from schoolbloc import db

log = logging.getLogger(__name__)


class Teacher(db.Model):
    """
    ORM object for teachers stored in the database

    A teacher uses their associated user object to log in to the app.
    The teacher object holds teacher specific info for teacher users.
    """
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", backref="teacher")

