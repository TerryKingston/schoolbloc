import logging
from schoolbloc import db
from sqlalchemy.ext.associationproxy import association_proxy

log = logging.getLogger(__name__)


class StudentGroup(db.Model):
    """
    ORM object for student groups stored in the database

    A Collection of students
    """
    __tablename__ = 'student_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    students = association_proxy('students_student_groups', 'student')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }
