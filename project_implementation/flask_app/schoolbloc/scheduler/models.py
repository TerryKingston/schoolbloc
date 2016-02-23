import logging
from schoolbloc import db
from sqlalchemy.ext.associationproxy import association_proxy

log = logging.getLogger(__name__)


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


class Course(db.Model, SqlalchemySerializer):
    """
    ORM object for courses stored in the database

    A course is a specific learning area (i.e. Algebra III)
    """
    __tablename__ = 'courses'
    __restconstraints__ = ['courses_student_group', 'courses_students', 'courses_subjects', 'courses_timeblocks',
                           'courses_teachers', 'classrooms_courses']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    duration = db.Column(db.Integer) # optional duration, will use global default if not specified
    max_student_count = db.Column(db.Integer)
    min_student_count = db.Column(db.Integer)
    avail_start_time = db.Column(db.Integer)
    avail_end_time = db.Column(db.Integer)

    def __str__(self):
        return "{} {}".format(self.name, self.duration, self.max_student_count, self.min_student_count,
                              self.avail_start_time, self.avail_end_time)


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
    priority = db.Column(db.String(128), nullable=False)
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
    priority = db.Column(db.String(128), nullable=False)
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
    priority = db.Column(db.String(128), nullable=False)
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
    __restconstraints__ = ['classrooms_teachers', 'classrooms_courses', 'classrooms_timeblocks']
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, nullable=False, unique=True)  # user assigned room number
    max_student_count = db.Column(db.Integer)
    avail_start_time = db.Column(db.Integer)
    avail_end_time = db.Column(db.Integer)

    def __str__(self):
        return "{} {}".format(self.room_number, self.max_student_count, self.avail_end_time, self.avail_start_time)


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
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False)
    classroom = db.relationship("Classroom", backref="classrooms_teachers")
    teacher = db.relationship("Teacher", backref="classrooms_teachers")


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
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False)
    classroom = db.relationship("Classroom", backref="classrooms_courses")
    course = db.relationship("Course", backref="classrooms_courses")


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


class StudentGroup(db.Model, SqlalchemySerializer):
    """
    ORM object for student groups stored in the database

    A Collection of students
    """
    __tablename__ = 'student_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    students = association_proxy('students_student_groups', 'student')

class StudentGroupsSubject(db.Model, SqlalchemySerializer):
    """
    ORM object for linking table between student_groups and subjects 
    """
    __tablename__ = 'student_groups_subjects'
    id = db.Column(db.Integer, primary_key=True)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False)
    student_group = db.relationship("StudentGroup", backref="student_groups_subjects")
    subject = db.relationship("Subject", backref="student_groups_subjects")


class Student(db.Model, SqlalchemySerializer):
    """
    ORM object for students stored in the database

    A student uses their associated user object to log in to
    the app. The Student object holds student specific info for student
    users.
    """
    __tablename__ = 'students'
    __restconstraints__ = ['students_student_group', 'students_timeblocks', 'subjects_students']
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", backref="student")

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


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

class StudentsSubject(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between students and subjects
    """
    __tablename__ = 'subjects_students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    student = db.relationship("Student", backref="students_subjects")
    subject = db.relationship("Subject", backref="students_subjects")


class Subject(db.Model, SqlalchemySerializer):
    """
    ORM object for subjects stored in the database

    A subject is a group of courses
    """
    __tablename__ = 'subjects'
    __restconstraints__ = ['courses_subjects', 'student_groups_subjects', 'subjects_students', 'subjects_timeblocks']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __str__(self):
        return "{} {}".format(self.name)

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
    avail_start_time = db.Column(db.Integer)
    avail_end_time = db.Column(db.Integer)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)
    

class CoursesTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between courses and timeblocks
    """
    __tablename__= 'courses_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False)
    course = db.relationship("Course", backref='courses_timeblocks')
    timeblock = db.relationship("Timeblock", backref='courses_timeblocks')


class ClassroomsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between classrooms and timeblocks
    """
    __tablename__= 'classrooms_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False)
    classroom = db.relationship("Classroom", backref='classrooms_timeblocks')
    timeblock = db.relationship("Timeblock", backref='classrooms_timeblocks')


class StudentGroupsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between classrooms and timeblocks
    """
    __tablename__= 'student_groups_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False)
    student_group = db.relationship("StudentGroup", backref='student_groups_timeblocks')
    timeblock = db.relationship("Timeblock", backref='student_groups_timeblocks')


class StudentsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between classrooms and timeblocks
    """
    __tablename__= 'students_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False)
    student = db.relationship("Student", backref='students_timeblocks')
    timeblock = db.relationship("Timeblock", backref='students_timeblocks')


class SubjectsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between subjects and timeblocks
    """
    __tablename__= 'subjects_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False)
    subject = db.relationship("Subject", backref='subjects_timeblocks')
    timeblock = db.relationship("Timeblock", backref='subjects_timeblocks')

class TeachersTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between teachers and timeblocks
    """
    __tablename__= 'teachers_timeblocks'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False)
    teacher = db.relationship("Teacher", backref='teachers_timeblocks')
    timeblock = db.relationship("Timeblock", backref='teachers_timeblocks')


class Timeblock(db.Model, SqlalchemySerializer):
    """
    ORM object for time blocks stored in the database

    A time block represents a continuous block of time in one 24hr period.
    The start time and end time are represented in 24h time as integers with 
    minute granularity (i.e. the value 1600 is 4 o'clock PM).
    """
    __tablename__ = 'timeblocks'
    __restconstraints__ = ['classrooms_timeblock', 'courses_timeblocks', 'students_timeblocks', 'student_groups_timeblocks', 'teachers_timeblocks']
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return "{} {}".format(self.start_time, self.end_time)