import logging
from schoolbloc import db
from schoolbloc.teachers.models import Teacher
from schoolbloc.students.models import Student
from schoolbloc.student_groups.models import StudentGroup
from schoolbloc.subjects.models import Subject


log = logging.getLogger(__name__)


class CourseError(Exception):
    pass


class Course(db.Model):
    """
    ORM object for courses stored in the database

    A course is a specific learning area (i.e. Algebra III)
    """
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    max_student_count = db.Column(db.Integer)
    min_student_count = db.Column(db.Integer)

    def __init__(self, name, max_student_count=None, min_student_count=None):
        self.name = name
        self.max_student_count = max_student_count
        self.min_student_count = min_student_count
        db.session.add(self)
        db.session.commit()
        log.info('added new course: {}'.format(name))

    def __repr__(self):
        return "<name={} max_student_count={} min_student_count={}>".format(
            self.name, self.max_student_count, self.min_student_count)

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class CoursesStudentError(Exception):
    pass


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

    def __init__(self, course_id, student_id, active=True):
        # we want to verify the given id's are actually present in the DB
        if not Course.query.get(course_id):
            raise CoursesStudentError("The course_id {} does not exist in the "
                                      "db".format(course_id))

        if not Student.query.get(student_id):
            raise CoursesStudentError("The student_id {} does not exist in the "
                                      "db".format(student_id))

        self.course_id = course_id
        self.student_id = student_id
        self.active = active
        db.session.add(self)
        db.session.commit()
        log.info('added new CoursesStudent: {} <--> {} {}'.format(
                 self.course.room_number, self.student.first_name, self.student.last_name))

    def __repr__(self):
        return "<course_id={} student_id={}>".format(self.course_id, self.student_id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class CoursesTeacherError(Exception):
    pass


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

    def __init__(self, course_id, teacher_id, active=True):
        # we want to verify the given id's are actually present in the DB
        if not Course.query.get(course_id):
            raise CoursesTeacherError("The course_id {} does not exist in the "
                                      "db".format(course_id))

        if not Teacher.query.get(teacher_id):
            raise CoursesTeacherError("The teacher_id {} does not exist in the "
                                      "db".format(teacher_id))

        self.course_id = course_id
        self.teacher_id = teacher_id
        self.active = active
        db.session.add(self)
        db.session.commit()
        log.info('added new CoursesTeacher: {} <--> {} {}'.format(
                 self.course.room_number, self.teacher.first_name, self.teacher.last_name))

    def __repr__(self):
        return "<course_id={} teacher_id={}>".format(self.course_id, self.teacher_id)

    def delete(self):
        db.sesson.delete(self)
        db.session.commit()


class CoursesStudentGroupError(Exception):
    pass


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

    def __init__(self, course_id, student_group_id, active=True):
        # we want to verify the given id's are actually present in the DB
        if not Course.query.get(course_id):
            raise CoursesStudentGroupError("The course_id {} does not exist in "
                                           "the db".format(course_id))

        if not StudentGroup.query.get(student_group_id):
            raise CoursesStudentGroupError("The student_group_id {} does not exist "
                                           "in the db".format(student_group_id))

        self.course_id = course_id
        self.student_group_id = student_group_id
        self.active = active
        db.session.add(self)
        db.session.commit()
        log.info('added new CoursesStudentGroup: {} <--> {} {}'.format(
                 self.course.room_number, self.student_group.name))

    def __repr__(self):
        return "<course_id={} student_group_id={}>".format(self.course_id,
                                                           self.student_group_id)

    def delete(self):
        db.sesson.delete(self)
        db.session.commit()


class CoursesSubjectError(Exception):
    pass


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

    def __init__(self, course_id, subject_id, active=True):
        # we want to verify the given id's are actually present in the DB
        if not Course.query.get(course_id):
            raise CoursesSubjectError("The course_id {} does not exist in the "
                                      "db".format(course_id))

        if not Subject.query.get(subject_id):
            raise CoursesSubjectError("The subject_id {} does not exist in the "
                                      "db".format(subject_id))

        self.course_id = course_id
        self.subject_id = subject_id
        self.active = active
        db.session.add(self)
        db.session.commit()
        log.info('added new CoursesSubject: {} <--> {} {}'.format(
                 self.course.room_number, self.subject.name))

    def __repr__(self):
        return "<course_id={} subject_id={}>".format(self.course_id, self.subject_id)

    def delete(self):
        db.sesson.delete(self)
        db.session.commit()
