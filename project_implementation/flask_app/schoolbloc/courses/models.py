import logging
from schoolbloc import db


log = logging.getLogger(__name__)


class Course(db.Model):
    """
    ORM object for courses stored in the database

    A course is a specific learning area (i.e. Algebra III)
    """
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    duration = db.Column(db.Integer) # optional duration, will use global default if not specified
    max_student_count = db.Column(db.Integer)
    min_student_count = db.Column(db.Integer)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'duration': self.duration,
            'max_student_count': self.max_student_count,
            'min_student_count': self.min_student_count,
        }


class CoursesStudent(db.Model):
    """
    ORM object for linking table between courses and students tables

    A CoursesStudent describes the relationship constraints
    between a course and a student for the scheduler.

    The actual assignment of a course to a student happens in
    the Class object.
    """
    __tablename__ = 'courses_students'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    student = db.relationship("Student", backref="courses_students")
    course = db.relationship("Course", backref="courses_students")


class CoursesTeacher(db.Model):
    """
    ORM object for linking table between courses and teachers tables

    A CoursesTeacher describes the relationship constraints
    between a course and a teacher for the scheduler.

    The actual assignment of a course to a teacher happens in
    the Class object.
    """
    __tablename__ = 'courses_teachers'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    teacher = db.relationship("Teacher", backref="courses_teachers")
    course = db.relationship("Course", backref="courses_teachers")


class CoursesStudentGroup(db.Model):
    """
    ORM object for linking table between courses and student groups tables

    A CoursesStudentGroup describes the relationship constraints
    between a course and a student group for the scheduler.

    The actual assignment of a course to a student group happens in
    the Class object.
    """
    __tablename__ = 'courses_student_groups'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    student_group = db.relationship("StudentGroup", backref="courses_student_groups")
    course = db.relationship("Course", backref="courses_student_groups")


class CoursesSubject(db.Model):
    """
    ORM object for linking table between courses and subjects tables

    A CoursesSubject describes the relationship constraints
    between a course and a subject for the scheduler.

    The actual assignment of a course to a subject happens in
    the Class object.
    """
    __tablename__ = 'courses_subjects'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    subject = db.relationship("Subject", backref="courses_subjects")
    course = db.relationship("Course", backref="courses_subjects")
