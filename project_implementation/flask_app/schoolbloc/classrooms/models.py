import logging
from schoolbloc import db

log = logging.getLogger(__name__)


class Serializer:
    """
    Provides a base model for our database tables and constraints. This
    provides a serialize method that will be utilized by our rest endpoints
    """
    def serialize(self):
        results = {}
        columns = self.__table__.columns.values()
        for column in columns:
            results[column.name] = getattr(self, column.name)
        return results


class Classroom(db.Model, Serializer):
    """
    ORM object for classrooms stored in the database

    A classroom object represents a physical classroom in
    a school building.
    """
    __tablename__ = 'classrooms'
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, nullable=False, unique=True)  # user assigned room number
    max_student_count = db.Column(db.Integer)


class ClassroomsTeacher(db.Model):
    """
    ORM object for linking table between classrooms and teachers tables

    A ClassroomsTeacher describes the relationship constraints
    between a classroom and a teacher for the scheduler.

    The actual assignment of a classroom to a teacher happens in
    the Class object.
    """
    __tablename__ = 'classrooms_teachers'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    classroom = db.relationship("Classroom", backref="classrooms_teachers")
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    teacher = db.relationship("Teacher", backref="classrooms_teachers")
    active = db.Column(db.Boolean, nullable=False, default=True)


class ClassroomsCourse(db.Model):
    """
    ORM object for linking table between classrooms and teachers tables

    A ClassroomsCourse describes the relationship constraints
    between a classroom and teacher for the scheduler.

    The actual assignement of a classroom to a course happens in the Class object
    """
    __tablename__ = 'classrooms_courses'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    classroom = db.relationship("Classroom", backref="classrooms_courses")
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    course = db.relationship("Course", backref="classrooms_courses")
    active = db.Column(db.Boolean, nullable=False, default=True)
