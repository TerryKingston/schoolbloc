import logging
from schoolbloc import db
from sqlalchemy.ext.associationproxy import association_proxy

log = logging.getLogger(__name__)


class SqlalchemySerializer:
    """
    Provides a base model for our database tables and constraints. This
    provides a serialize method that will be utilized by our rest endpoints
    """
    def serialize(self):
        results = {}

        columns = self.__table__.columns.values()
        for column in columns:
            results[column.name] = getattr(self, column.name)

        relationships = self.__mapper__.relationships.keys()
        for name in relationships:
            try:
                results[name] = [x.serialize() for x in getattr(self, name)]
            except TypeError:
                # Only grab one to many relationships (infinite loop otherwise)
                pass
        return results


class Course(db.Model, SqlalchemySerializer):
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


class CoursesStudent(db.Model, SqlalchemySerializer):
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


class CoursesTeacher(db.Model, SqlalchemySerializer):
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


class CoursesStudentGroup(db.Model, SqlalchemySerializer):
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


class CoursesSubject(db.Model, SqlalchemySerializer):
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


class Classroom(db.Model, SqlalchemySerializer):
    """
    ORM object for classrooms stored in the database

    A classroom object represents a physical classroom in
    a school building.
    """
    __tablename__ = 'classrooms'
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, nullable=False, unique=True)  # user assigned room number
    max_student_count = db.Column(db.Integer)


class ClassroomsTeacher(db.Model, SqlalchemySerializer):
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


class ClassroomsCourse(db.Model, SqlalchemySerializer):
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


class Schedule(db.Model, SqlalchemySerializer):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    # backref scheduled_classes


class ScheduledClass(db.Model, SqlalchemySerializer):
    """
    ORM object for scheduled_class stored in the database

    A scheduled class is a combination of Teacher, Time, Classroom, Course, and Students
    """
    __tablename__ = 'scheduled_classes'
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    schedule = db.relationship('Schedule', backref='scheduled_classes')
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    classroom = db.relationship("Classroom", backref="scheduled_class")
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    teacher = db.relationship("Teacher", backref="scheduled_class")
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    course = db.relationship("Course", backref="scheduled_class")
    students = association_proxy('scheduled_classes_student', 'student')
    start_time = db.Column(db.Integer, nullable=False) # time in 24 hr format (i.e. 1454)
    end_time = db.Column(db.Integer, nullable=False)

    def __init__(self, schedule_id, course_id, classroom_id, teacher_id, start_time, end_time):
        # validate start and end time
        if start_time < 0 or start_time > 2359 or end_time < 0 or end_time > 2359:
            raise Exception("start_time and end_time must be between 0 and 2359")

        self.schedule_id = schedule_id
        self.start_time = start_time
        self.end_time = end_time
        self.course_id = course_id
        self.classroom_id = classroom_id
        self.teacher_id = teacher_id


class ScheduledClassesStudent(db.Model, SqlalchemySerializer):
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


class StudentGroup(db.Model, SqlalchemySerializer):
    """
    ORM object for student groups stored in the database

    A Collection of students
    """
    __tablename__ = 'student_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)


class Student(db.Model, SqlalchemySerializer):
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


class StudentsStudentGroup(db.Model, SqlalchemySerializer):
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


class Subject(db.Model, SqlalchemySerializer):
    """
    ORM object for subjects stored in the database

    A subject is a group of courses
    """
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Teacher(db.Model, SqlalchemySerializer):
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
