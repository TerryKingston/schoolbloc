import logging
from schoolbloc import db, app
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.associationproxy import association_proxy

log = logging.getLogger(__name__)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """ Turn on foreign key support if using sqlite3 """
    if app.config.get('SQLALCHEMY_DATABASE_URI').startswith('sqlite'):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class SqlalchemySerializer:
    """
    Provides a base model for our database tables and constraints. This
    provides a serialize method that will be utilized by our rest endpoints
    """
    def serialize(self, base_set=None):
        results = {}

        # Serialize the list of columns. Don't print out foreign keys, as those
        # get dereference into their full objects bellow
        columns = self.__table__.columns.values()
        for column in columns:
            if not column.foreign_keys:
                results[column.name] = getattr(self, column.name)
        return results


########
# Facts
########

class Classroom(db.Model, SqlalchemySerializer):
    """
    ORM object for classrooms stored in the database

    A classroom object represents a physical classroom in
    a school building.
    """
    __tablename__ = 'classrooms'
    __restconstraints__ = ['classrooms_teachers', 'classrooms_courses', 'classrooms_timeblocks',
                           'classrooms_subjects']
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, nullable=False, unique=True)  # user assigned room number
    classrooms_subjects = db.relationship("ClassroomsSubject", back_populates="classroom", passive_deletes=True)

    def __str__(self):
        return "{}".format(self.room_number)


class Course(db.Model, SqlalchemySerializer):
    """
    ORM object for courses stored in the database

    A course is a specific learning area (i.e. Algebra III)
    """
    __tablename__ = 'courses'
    __restconstraints__ = ['courses_student_groups', 'courses_students', 'courses_subjects', 'courses_timeblocks',
                           'courses_teachers', 'classrooms_courses']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    duration = db.Column(db.Integer) # optional duration, will use global default if not specified
    max_student_count = db.Column(db.Integer)
    min_student_count = db.Column(db.Integer)

    def __str__(self):
        return "{}".format(self.name)


class Student(db.Model, SqlalchemySerializer):
    """
    ORM object for students stored in the database

    A student uses their associated user object to log in to
    the app. The Student object holds student specific info for student
    users.
    """
    __tablename__ = 'students'
    __restconstraints__ = ['students_student_groups', 'students_timeblocks', 'students_subjects', 'courses_students',
                           'students_timeblocks', 'students_subjects']
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", backref="student")

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class StudentGroup(db.Model, SqlalchemySerializer):
    """
    ORM object for student groups stored in the database

    A Collection of students
    """
    __tablename__ = 'student_groups'
    __restconstraints__ = ['students_student_groups', 'student_groups_timeblocks',
                           'student_groups_subjects', 'courses_student_groups']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    students = association_proxy('students_student_groups', 'student')

    def __str__(self):
        return "{}".format(self.name)


class Subject(db.Model, SqlalchemySerializer):
    """
    ORM object for subjects stored in the database

    A subject is a group of courses
    """
    __tablename__ = 'subjects'
    __restconstraints__ = ['courses_subjects', 'student_groups_subjects', 'students_subjects', 'subjects_timeblocks',
                           'teachers_subjects', 'teachers_subjects', 'subjects_timeblocks', 'classrooms_subjects']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    classrooms_subjects = db.relationship("ClassroomsSubject", back_populates="subject", passive_deletes=True)

    def __str__(self):
        return "{}".format(self.name)


class Teacher(db.Model, SqlalchemySerializer):
    """
    ORM object for teachers stored in the database

    A teacher uses their associated user object to log in to the app.
    The teacher object holds teacher specific info for teacher users.
    """
    __tablename__ = 'teachers'
    __restconstraints__ = ['classrooms_teachers', 'teachers_timeblocks', 'courses_teachers',
                           'teachers_subjects']
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", backref="teacher")
    avail_start_time = db.Column(db.Integer)
    avail_end_time = db.Column(db.Integer)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class Timeblock(db.Model, SqlalchemySerializer):
    """
    ORM object for time blocks stored in the database

    A time block represents a continuous block of time in one 24hr period.
    The start time and end time are represented in 24h time as integers with
    minute granularity (i.e. the value 1600 is 4 o'clock PM).
    """
    __tablename__ = 'timeblocks'
    __restconstraints__ = ['classrooms_timeblocks', 'courses_timeblocks', 'students_timeblocks',
                           'student_groups_timeblocks', 'teachers_timeblocks', 'subjects_timeblocks']
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return "{} {}".format(self.start_time, self.end_time)


##############
# Constraints
##############

class ClassroomsCourse(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between classrooms and teachers tables """
    __tablename__ = 'classrooms_courses'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    classroom = db.relationship("Classroom", backref="classrooms_courses")
    course = db.relationship("Course", backref="classrooms_courses")

    def __str__(self):
        return "{} {}".format(self.classroom, self.course)


class ClassroomsSubject(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between classrooms and subjects tables """
    __tablename__ = 'classrooms_subjects'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id', ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete="CASCADE"), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    classroom = db.relationship("Classroom", back_populates="classrooms_subjects")
    subject = db.relationship("Subject", back_populates="classrooms_subjects")

    def __str__(self):
        return "{} {} {}".format(self.classroom, self.subject, self.priority)


class ClassroomsTeacher(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between classrooms and teachers tables """
    __tablename__ = 'classrooms_teachers'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    classroom = db.relationship("Classroom", backref="classrooms_teachers")
    teacher = db.relationship("Teacher", backref="classrooms_teachers")

    def __str__(self):
        return "{} {}".format(self.classroom, self.teacher)


class ClassroomsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between classrooms and timeblocks
    """
    __tablename__= 'classrooms_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    classroom = db.relationship("Classroom", backref='classrooms_timeblocks')
    timeblock = db.relationship("Timeblock", backref='classrooms_timeblocks')

    def __str__(self):
        return "{} {}".format(self.classroom, self.timeblock)


class CoursesStudent(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between courses and students tables """
    __tablename__ = 'courses_students'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    student = db.relationship("Student", backref="courses_students")
    course = db.relationship("Course", backref="courses_students")

    def __str__(self):
        return "{} {}".format(self.student, self.course)


class CoursesStudentGroup(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between courses and student groups tables """
    __tablename__ = 'courses_student_groups'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    student_group = db.relationship("StudentGroup", backref="courses_student_groups")
    course = db.relationship("Course", backref="courses_student_groups")

    def __str__(self):
        return "{} {} {}".format(self.student_group, self.course, self.priority)


class CoursesSubject(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between courses and subjects tables """
    __tablename__ = 'courses_subjects'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    subject = db.relationship("Subject", backref="courses_subjects")
    course = db.relationship("Course", backref="courses_subjects")

    def __str__(self):
        return "{} {}".format(self.subject, self.course)


class CoursesTimeblock(db.Model, SqlalchemySerializer):
    """ ORM Object for linking table between courses and timeblocks """
    __tablename__= 'courses_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    course = db.relationship("Course", backref='courses_timeblocks')
    timeblock = db.relationship("Timeblock", backref='courses_timeblocks')

    def __str__(self):
        return "{} {}".format(self.course, self.timeblock)


class CoursesTeacher(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between courses and teachers tables """
    __tablename__ = 'courses_teachers'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    teacher = db.relationship("Teacher", backref="courses_teachers")
    course = db.relationship("Course", backref="courses_teachers")

    def __str__(self):
        return "{} {}".format(self.teacher, self.course)


class StudentGroupsSubject(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between student_groups and subjects """
    __tablename__ = 'student_groups_subjects'
    id = db.Column(db.Integer, primary_key=True)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    student_group = db.relationship("StudentGroup", backref="student_groups_subjects")
    subject = db.relationship("Subject", backref="student_groups_subjects")

    def __str__(self):
        return "{} {}".format(self.student_group, self.subject)


class StudentGroupsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between classrooms and timeblocks
    """
    __tablename__= 'student_groups_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    student_group = db.relationship("StudentGroup", backref='student_groups_timeblocks')
    timeblock = db.relationship("Timeblock", backref='student_groups_timeblocks')

    def __str__(self):
        return "{} {}".format(self.student_group, self.timeblock)


class StudentsStudentGroup(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between students and student_groups tables """
    __tablename__ = 'students_student_groups'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    priority = db.Column(db.String(128), nullable=False, default='low')
    active = db.Column(db.Boolean, nullable=False, default=True)
    student = db.relationship("Student", backref="students_student_groups")
    student_group = db.relationship("StudentGroup", backref="students_student_groups")

    def __str__(self):
        return "{} {}".format(self.student, self.student_group)


class StudentsSubject(db.Model, SqlalchemySerializer):
    """ ORM Object for linking table between students and subjects """
    __tablename__ = 'subjects_students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    priority = db.Column(db.String(128), nullable=False, default='low')
    active = db.Column(db.Boolean, nullable=False, default=True)
    student = db.relationship("Student", backref="students_subjects")
    subject = db.relationship("Subject", backref="students_subjects")

    def __str__(self):
        return "{} {}".format(self.student, self.subject)


class StudentsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between classrooms and timeblocks
    """
    __tablename__= 'students_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    student = db.relationship("Student", backref='students_timeblocks')
    timeblock = db.relationship("Timeblock", backref='students_timeblocks')

    def __str__(self):
        return "{} {}".format(self.student, self.timeblock)


class SubjectsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between subjects and timeblocks
    """
    __tablename__= 'subjects_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    subject = db.relationship("Subject", backref='subjects_timeblocks')
    timeblock = db.relationship("Timeblock", backref='subjects_timeblocks')

    def __str__(self):
        return "{} {}".format(self.subject, self.timeblock)


class TeachersSubject(db.Model, SqlalchemySerializer):
    __tablename__ = 'teachers_subjects'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    teacher = db.relationship("Teacher", backref="teachers_subjects")
    subject = db.relationship("Subject", backref="teachers_subjects")

    def __str__(self):
        return "{} {}".format(self.teacher, self.subject)


class TeachersTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between teachers and timeblocks
    """
    __tablename__= 'teachers_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    teacher = db.relationship("Teacher", backref='teachers_timeblocks')
    timeblock = db.relationship("Timeblock", backref='teachers_timeblocks')

    def __str__(self):
        return "{} {}".format(self.teacher, self.timeblock)


############
# Schedules
############

class Schedule(db.Model, SqlalchemySerializer):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    # backref scheduled_classes

    def __str__(self):
        return "{}".format(self.name)


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

    def __repr__(self):
        return "<id: {}, start: {}, end: {}, course_id: {}, classroom_id: {}, teacher_id: {}>".format(
                self.id, self.start_time, self.end_time, self.course_id, self.classroom_id, self.teacher_id)


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

    def __str__(self):
        return "{} {}".format(self.scheduled_class, self.student)