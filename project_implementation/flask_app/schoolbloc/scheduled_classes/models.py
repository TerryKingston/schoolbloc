import logging
from schoolbloc import db
from sqlalchemy.ext.associationproxy import association_proxy

log = logging.getLogger(__name__)


class ScheduledClassError(Exception):
    pass


class ScheduledClass(db.Model):
    """
    ORM object for scheduled_class stored in the database

    A scheduled class is a combination of Teacher, Time, Classroom, Course, and Students
    """
    __tablename__ = 'scheduled_classes'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    classroom = db.relationship("Classroom", backref="scheduled_class")
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    teacher = db.relationship("Teacher", backref="scheduled_class")
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    course = db.relationship("Course", backref="scheduled_class")
    students = association_proxy('scheduled_classes_student', 'student')
    start_time = db.Column(db.Integer, nullable=False) # time in 24 hr format (i.e. 1454)
    end_time = db.Column(db.Integer, nullable=False)

    def __init__(self, course_id, classroom_id, teacher_id, start_time, end_time):
        # validate start and end time
        if start_time < 0 or start_time > 2359 or end_time < 0 or end_time > 2359:
            raise ScheduledClassError(" start_time and end_time must be between 0 and 2359 ")

        self.start_time = start_time
        self.end_time = end_time
        self.course_id = course_id
        self.classroom_id = classroom_id
        self.teacher_id = teacher_id


class ScheduledClassesStudent(db.Model):
    """
    ORM object for linking table between schedule classes and students

    This link means the student is a member of the scheduled class
    """
    __tablename__ = 'scheduled_classes_students'
    id = db.Column(db.Integer, primary_key=True)
    scheduled_class_id = db.Column(db.Integer, db.ForeignKey('scheduled_classes.id'), nullable=False)
    scheduled_class = db.relationship("ScheduledClass", backref="scheduled_classes_student")
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    student = db.relationship("Student", backref="scheduled_classes_student")
