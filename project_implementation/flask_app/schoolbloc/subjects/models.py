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

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }

class SubjectsStudentGroup(db.Model):
    """
    ORM object for mapping from Subject to Student Group
    """
    __tablename__ = 'subjects_student_groups'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    subject = db.relationship("Subject", backref="subjects_student_groups")
    course = db.relationship("StudentGroup", backref="subjects_student_groups")
