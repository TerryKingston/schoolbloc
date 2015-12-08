import logging
from schoolbloc import db

log = logging.getLogger(__name__)


class Student(db.Model):
    """
    ORM object for students stored in the database

    A student uses their associated user object to log in to
    the app. The Student object holds student specific info for student
    users.
    """
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", backref="student")

    def serialize(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_id': self.user_id,
        }


class StudentsStudentGroup(db.Model):
    """
    ORM object for linking table between students and student_groups tables

    A StudentsStudentGroup describes the relationship constraints
    between a student and a student group for the scheduler.

    The actual assignment of a student to a student group happens in
    the Class object.
    """
    __tablename__ = 'students_student_groups'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    student = db.relationship("Student", backref="students_student_groups")
    student_group = db.relationship("StudentGroup", backref="students_student_groups")

    def serialize(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_group_id': self.student_group_id,
            'active': self.active,
        }
