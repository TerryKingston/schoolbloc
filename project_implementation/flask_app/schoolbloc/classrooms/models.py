import logging
from sqlalchemy.exc import IntegrityError
from schoolbloc.teachers.models import Teacher
from schoolbloc.courses.models import Course
from schoolbloc import db

log = logging.getLogger(__name__)


class ClassroomError(Exception):
    pass


class Classroom(db.Model):
    """
    ORM object for classrooms stored in the database

    A classroom object represents a physical classroom in
    a school building.
    """
    __tablename__ = 'classrooms'
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, nullable=False, unique=True)  # user assigned room number
    max_student_count = db.Column(db.Integer)

    def __init__(self, room_number, max_student_count=None):
        self.room_number = room_number
        if max_student_count:
            self.max_student_count = max_student_count

        # the room number could be a duplicate
        try:
            db.session.add(self)
            db.session.commit()
            log.info('added new classroom: {}'.format(room_number))
        except IntegrityError:
            db.session.rollback()
            raise ClassroomError("The room number {} already exists in the db"
                                 .format(room_number))

    def __repr__(self):
        return "<room_number={} max_student_count={}>".format(self.room_number,
                                                              self.max_student_count)

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class ClassroomsTeacherError(Exception):
    pass


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

    def __init__(self, classroom_id, teacher_id, active=None):
        # we want to verify the given id's are actually present in the DB
        if not Classroom.query.get(classroom_id):
            raise ClassroomsTeacherError("The classroom_id {} does not exist in "
                                         "the db".format(classroom_id))

        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            raise ClassroomsTeacherError("The teacher_id {} does not exist in "
                                         "the db".format(teacher_id))

        self.classroom_id = classroom_id
        self.teacher_id = teacher_id
        if active:
            self.active = active

        db.session.add(self)
        db.session.commit()
        log.info('added new ClassroomsTeacher: {} <--> {} {}'.format(
            self.classroom.room_number,
            teacher.first_name,
            teacher.last_name))

    def __repr__(self):
        return "<classroom_id={} teacher_id={}>".format(self.classroom_id,
                                                        self.teacher_id)

    def delete(self):
        db.sesson.delete(self)
        db.session.commit()


class ClassroomsCourseError(Exception):
    pass


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

    def __init__(self, classroom_id, course_id, active=None):
        # we want to verify the given id's are actually present in the DB
        if not Classroom.query.get(classroom_id):
            raise ClassroomsCourseError("The classroom_id {} does not exist in "
                                        "the db".format(classroom_id))

        course = Course.query.get(course_id)
        if not course:
            raise ClassroomsCourseError("The course_id {} does not exist in the "
                                        "db".format(course_id))

        self.classroom_id = classroom_id
        self.course_id = course_id
        if active:
            self.active = active

        db.session.add(self)
        db.session.commit()
        log.info('acced new ClassroomsCourse: {} <--> {} {}'.format(
                 self.classroom.room_number, course.name))

    def __repr__(self):
        return "<classroom_id={} course_id={}>".format(self.classroom_id,
                                                       self.course_id)

    def delete(self):
        db.sesson.delete(self)
        db.session.commit()
