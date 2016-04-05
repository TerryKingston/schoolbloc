import logging
from collections import OrderedDict

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
    def serialize(self):
        results = OrderedDict()

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
    # Name and rest constraints for API generation
    __tablename__ = 'classrooms'
    __restconstraints__ = ['classrooms_teachers', 'classrooms_courses',
                           'classrooms_subjects', 'classrooms_timeblocks']

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, nullable=False, unique=True)

    # Relationships
    classrooms_subjects = db.relationship("ClassroomsSubject",
                                          back_populates="classroom",
                                          passive_deletes=True)
    classrooms_courses = db.relationship("ClassroomsCourse",
                                         back_populates="classroom",
                                         passive_deletes=True)
    classrooms_teachers = db.relationship("ClassroomsTeacher",
                                          back_populates="classroom",
                                          passive_deletes=True)
    classrooms_timeblocks = db.relationship("ClassroomsTimeblock",
                                            back_populates="classroom",
                                            passive_deletes=True)
    scheduled_class = db.relationship("ScheduledClass",
                                      back_populates="classroom",
                                      passive_deletes=True)

    def __str__(self):
        return "{}".format(self.room_number)


class Course(db.Model, SqlalchemySerializer):
    """
    ORM object for courses stored in the database

    A course is a specific learning area (i.e. Algebra III)
    """
    # Name and rest constraints for API generation
    __tablename__ = 'courses'
    __restconstraints__ = ['courses_subjects', 'courses_teachers',
                            'courses_students', 'courses_student_groups',
                            'classrooms_courses', 'courses_timeblocks']

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    min_student_count = db.Column(db.Integer)
    max_student_count = db.Column(db.Integer)
    duration = db.Column(db.Integer)  # optional duration, will use global default if not specified

    # Relationships
    classrooms_courses = db.relationship("ClassroomsCourse",
                                         back_populates="course",
                                         passive_deletes=True)
    courses_students = db.relationship("CoursesStudent",
                                       back_populates="course",
                                       passive_deletes=True)
    courses_student_groups = db.relationship("CoursesStudentGroup",
                                             back_populates="course",
                                             passive_deletes=True)
    courses_subjects = db.relationship("CoursesSubject",
                                       back_populates="course",
                                       passive_deletes=True)
    courses_timeblocks = db.relationship("CoursesTimeblock",
                                         back_populates="course",
                                         passive_deletes=True)
    courses_teachers = db.relationship("CoursesTeacher",
                                       back_populates="course",
                                       passive_deletes=True)
    scheduled_class = db.relationship("ScheduledClass",
                                      back_populates="course",
                                      passive_deletes=True)

    def __str__(self):
        return "{}".format(self.name)


class Student(db.Model, SqlalchemySerializer):
    """
    ORM object for students stored in the database

    A student uses their associated user object to log in to
    the app. The Student object holds student specific info for student
    users.
    """
    # Name and rest constraints for API generation
    __tablename__ = 'students'
    __restconstraints__ = ['students_student_groups', 'courses_students',
                           'students_subjects', 'students_timeblocks']

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)

    # Relationships
    user = db.relationship("User", backref="student")
    courses_students = db.relationship("CoursesStudent",
                                       back_populates="student",
                                       passive_deletes=True)
    students_student_groups = db.relationship("StudentsStudentGroup",
                                              back_populates="student",
                                              passive_deletes=True)
    students_subjects = db.relationship("StudentsSubject",
                                        back_populates="student",
                                        passive_deletes=True)
    students_timeblocks = db.relationship("StudentsTimeblock",
                                          back_populates="student",
                                          passive_deletes=True)
    scheduled_classes_student = db.relationship("ScheduledClassesStudent",
                                                back_populates="student",
                                                passive_deletes=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class StudentGroup(db.Model, SqlalchemySerializer):
    """
    ORM object for student groups stored in the database

    A Collection of students
    """
    # Name and rest constraints for API generation
    __tablename__ = 'student_groups'
    __restconstraints__ = ['students_student_groups', 'courses_student_groups',
                           'student_groups_subjects', 'student_groups_timeblocks']

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    students = association_proxy('students_student_groups', 'student')

    # Relationships
    courses_student_groups = db.relationship("CoursesStudentGroup",
                                             back_populates="student_group",
                                             passive_deletes=True)
    student_groups_subjects = db.relationship("StudentGroupsSubject",
                                              back_populates="student_group",
                                              passive_deletes=True)
    student_groups_timeblocks = db.relationship("StudentGroupsTimeblock",
                                                back_populates="student_group",
                                                passive_deletes=True)
    students_student_groups = db.relationship("StudentsStudentGroup",
                                              back_populates="student_group",
                                              passive_deletes=True)

    def __str__(self):
        return "{}".format(self.name)


class Subject(db.Model, SqlalchemySerializer):
    """
    ORM object for subjects stored in the database

    A subject is a group of courses
    """
    # Name and rest constraints for API generation
    __tablename__ = 'subjects'
    __restconstraints__ = ['courses_subjects', 'teachers_subjects',
                           'students_subjects', 'student_groups_subjects',
                            'classrooms_subjects', 'subjects_timeblocks']

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    # Relationships
    classrooms_subjects = db.relationship("ClassroomsSubject",
                                          back_populates="subject",
                                          passive_deletes=True)
    courses_subjects = db.relationship("CoursesSubject",
                                       back_populates="subject",
                                       passive_deletes=True)
    student_groups_subjects = db.relationship("StudentGroupsSubject",
                                              back_populates="subject",
                                              passive_deletes=True)
    students_subjects = db.relationship("StudentsSubject",
                                        back_populates="subject",
                                        passive_deletes=True)
    subjects_timeblocks = db.relationship("SubjectsTimeblock",
                                          back_populates="subject",
                                          passive_deletes=True)
    teachers_subjects = db.relationship("TeachersSubject",
                                        back_populates="subject",
                                        passive_deletes=True)

    def __str__(self):
        return "{}".format(self.name)


class Teacher(db.Model, SqlalchemySerializer):
    """
    ORM object for teachers stored in the database

    A teacher uses their associated user object to log in to the app.
    The teacher object holds teacher specific info for teacher users.
    """
    # Name and rest constraints for API generation
    __tablename__ = 'teachers'
    __restconstraints__ = ['courses_teachers', 'teachers_subjects',
                           'classrooms_teachers', 'teachers_timeblocks']

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    avail_start_time = db.Column(db.Integer)
    avail_end_time = db.Column(db.Integer)
    user = db.relationship("User", backref="teacher")

    # Relationships
    classrooms_teachers = db.relationship("ClassroomsTeacher",
                                          back_populates="teacher",
                                          passive_deletes=True)
    courses_teachers = db.relationship("CoursesTeacher",
                                       back_populates="teacher",
                                       passive_deletes=True)
    teachers_subjects = db.relationship("TeachersSubject",
                                        back_populates="teacher",
                                        passive_deletes=True)
    teachers_timeblocks = db.relationship("TeachersTimeblock",
                                          back_populates="teacher",
                                          passive_deletes=True)
    scheduled_class = db.relationship("ScheduledClass",
                                        back_populates="teacher",
                                        passive_deletes=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class Timeblock(db.Model, SqlalchemySerializer):
    """
    ORM object for time blocks stored in the database

    A time block represents a continuous block of time in one 24hr period.
    The start time and end time are represented in 24h time as integers with
    minute granularity (i.e. the value 1600 is 4 o'clock PM).
    """
    # Name and rest constraints for API generation
    __tablename__ = 'timeblocks'
    __restconstraints__ = ['teachers_timeblocks','students_timeblocks',
                           'student_groups_timeblocks', 'courses_timeblocks',
                           'subjects_timeblocks', 'classrooms_timeblocks']

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)

    # Relationships
    classrooms_timeblocks = db.relationship("ClassroomsTimeblock",
                                            back_populates="timeblock",
                                            passive_deletes=True)
    courses_timeblocks = db.relationship("CoursesTimeblock",
                                         back_populates="timeblock",
                                         passive_deletes=True)
    student_groups_timeblocks = db.relationship("StudentGroupsTimeblock",
                                                back_populates="timeblock",
                                                passive_deletes=True)
    students_timeblocks = db.relationship("StudentsTimeblock",
                                          back_populates="timeblock",
                                          passive_deletes=True)
    subjects_timeblocks = db.relationship("SubjectsTimeblock",
                                          back_populates="timeblock",
                                          passive_deletes=True)
    teachers_timeblocks = db.relationship("TeachersTimeblock",
                                          back_populates="timeblock",
                                          passive_deletes=True)

    def __str__(self):
        return "{} {}".format(self.start_time, self.end_time)


##############
# Constraints
##############

class ClassroomsCourse(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between classrooms and teachers tables """
    __tablename__ = 'classrooms_courses'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    classroom = db.relationship("Classroom", back_populates="classrooms_courses")
    course = db.relationship("Course", back_populates="classrooms_courses")


class ClassroomsSubject(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between classrooms and subjects tables """
    __tablename__ = 'classrooms_subjects'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id', ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    classroom = db.relationship("Classroom", back_populates="classrooms_subjects")
    subject = db.relationship("Subject", back_populates="classrooms_subjects")


class ClassroomsTeacher(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between classrooms and teachers tables """
    __tablename__ = 'classrooms_teachers'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id', ondelete="CASCADE"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    classroom = db.relationship("Classroom", back_populates="classrooms_teachers")
    teacher = db.relationship("Teacher", back_populates="classrooms_teachers")


class ClassroomsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between classrooms and timeblocks
    """
    __tablename__ = 'classrooms_timeblocks'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id', ondelete="CASCADE"), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    classroom = db.relationship("Classroom", back_populates='classrooms_timeblocks')
    timeblock = db.relationship("Timeblock", back_populates='classrooms_timeblocks')


class CoursesStudent(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between courses and students tables """
    __tablename__ = 'courses_students'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    student = db.relationship("Student", back_populates="courses_students")
    course = db.relationship("Course", back_populates="courses_students")


class CoursesStudentGroup(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between courses and student groups tables """
    __tablename__ = 'courses_student_groups'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    student_group = db.relationship("StudentGroup", back_populates="courses_student_groups")
    course = db.relationship("Course", back_populates="courses_student_groups")


class CoursesSubject(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between courses and subjects tables """
    __tablename__ = 'courses_subjects'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    subject = db.relationship("Subject", back_populates="courses_subjects")
    course = db.relationship("Course", back_populates="courses_subjects")


class CoursesTimeblock(db.Model, SqlalchemySerializer):
    """ ORM Object for linking table between courses and timeblocks """
    __tablename__ = 'courses_timeblocks'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    course = db.relationship("Course", back_populates='courses_timeblocks')
    timeblock = db.relationship("Timeblock", back_populates='courses_timeblocks')


class CoursesTeacher(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between courses and teachers tables """
    __tablename__ = 'courses_teachers'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    teacher = db.relationship("Teacher", back_populates="courses_teachers")
    course = db.relationship("Course", back_populates="courses_teachers")


class StudentGroupsSubject(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between student_groups and subjects """
    __tablename__ = 'student_groups_subjects'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id', ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    student_group = db.relationship("StudentGroup", back_populates="student_groups_subjects")
    subject = db.relationship("Subject", back_populates="student_groups_subjects")


class StudentGroupsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between classrooms and timeblocks
    """
    __tablename__ = 'student_groups_timeblocks'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id', ondelete="CASCADE"), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    student_group = db.relationship("StudentGroup", back_populates='student_groups_timeblocks')
    timeblock = db.relationship("Timeblock", back_populates='student_groups_timeblocks')


class StudentsStudentGroup(db.Model, SqlalchemySerializer):
    """ ORM object for linking table between students and student_groups tables """
    __tablename__ = 'students_student_groups'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    active = db.Column(db.Boolean, nullable=False, default=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete="CASCADE"), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    student = db.relationship("Student", back_populates="students_student_groups")
    student_group = db.relationship("StudentGroup", back_populates="students_student_groups")


class StudentsSubject(db.Model, SqlalchemySerializer):
    """ ORM Object for linking table between students and subjects """
    __tablename__ = 'subjects_students'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    active = db.Column(db.Boolean, nullable=False, default=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    student = db.relationship("Student", back_populates="students_subjects")
    subject = db.relationship("Subject", back_populates="students_subjects")


class StudentsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between classrooms and timeblocks
    """
    __tablename__ = 'students_timeblocks'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete="CASCADE"), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    student = db.relationship("Student", back_populates='students_timeblocks')
    timeblock = db.relationship("Timeblock", back_populates='students_timeblocks')


class SubjectsTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between subjects and timeblocks
    """
    __tablename__ = 'subjects_timeblocks'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete="CASCADE"), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    subject = db.relationship("Subject", back_populates='subjects_timeblocks')
    timeblock = db.relationship("Timeblock", back_populates='subjects_timeblocks')


class TeachersSubject(db.Model, SqlalchemySerializer):
    __tablename__ = 'teachers_subjects'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    teacher = db.relationship("Teacher", back_populates="teachers_subjects")
    subject = db.relationship("Subject", back_populates="teachers_subjects")


class TeachersTimeblock(db.Model, SqlalchemySerializer):
    """
    ORM Object for linking table between teachers and timeblocks
    """
    __tablename__ = 'teachers_timeblocks'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(128), nullable=False, default='low')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete="CASCADE"), nullable=False)
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    teacher = db.relationship("Teacher", back_populates='teachers_timeblocks')
    timeblock = db.relationship("Timeblock", back_populates='teachers_timeblocks')


############
# Schedules
############

class Schedule(db.Model, SqlalchemySerializer):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    scheduled_classes = db.relationship("ScheduledClass", back_populates="schedule",
                                        passive_deletes=True)

    def __str__(self):
        return "{}".format(self.name)

    def serialize(self, expanded=False):
        ret = OrderedDict()
        ret['id'] = self.id
        ret['name'] = self.name
        ret['created_at'] = str(self.created_at)
        if expanded:
            ret['classes'] = [s.serialize() for s in self.scheduled_classes]
        return ret

    def student_serialize(self):
        ret = OrderedDict()
        ret['id'] = self.id
        ret['name'] = self.name
        ret['created_at'] = str(self.created_at)

        # This is a dict just for the sake of adding new classes for students
        # efficiently. When we return this, we will convert it back into a list
        # with just the values of the students in there (having an int as the
        # key is invalid json)
        students = {}
        for sch_class in self.scheduled_classes:
            for student in sch_class.students:
                if student.id not in students:
                    students[student.id] = OrderedDict()
                    students[student.id]['id'] = student.id
                    students[student.id]['first_name'] = student.first_name
                    students[student.id]['last_name'] = student.last_name
                    students[student.id]['classes'] = []

                students[student.id]['classes'].append({
                    'classroom': str(sch_class.classroom),
                    'classroom_id': sch_class.classroom.id,
                    'course': str(sch_class.course),
                    'course_id': sch_class.course_id,
                    'teacher': str(sch_class.teacher),
                    'teacher_id': sch_class.teacher_id,
                    'start_time': sch_class.start_time,
                    'end_time': sch_class.end_time,
                })

        # Where we convert it back into a list, for reasons mentioned above
        ret['students'] = [s for s in students.values()]
        return ret


class ScheduledClass(db.Model, SqlalchemySerializer):
    """
    ORM object for scheduled_class stored in the database

    A scheduled class is a combination of Teacher, Time, Classroom, Course, and Students
    """
    __tablename__ = 'scheduled_classes'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Integer, nullable=False)  # time in 24 hr format (i.e. 1454)
    end_time = db.Column(db.Integer, nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id', ondelete="CASCADE"), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id', ondelete="CASCADE"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"), nullable=False)

    schedule = db.relationship('Schedule', back_populates='scheduled_classes')
    classroom = db.relationship("Classroom", back_populates="scheduled_class")
    teacher = db.relationship("Teacher", back_populates="scheduled_class")
    course = db.relationship("Course", back_populates="scheduled_class")
    scheduled_classes_student = db.relationship("ScheduledClassesStudent",
                                                back_populates="scheduled_class",
                                                passive_deletes=True)

    students = association_proxy('scheduled_classes_student', 'student')

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

    def serialize(self):
        ret = OrderedDict()
        ret['id'] = self.id,
        ret['classroom'] = {'value': str(self.classroom), 'id': self.classroom_id}
        ret['course'] = {'value': str(self.course), 'id': self.course_id}
        ret['teacher'] = {'value': str(self.teacher), 'id': self.teacher_id}
        ret['students'] = [{'value': str(s), 'id': s.id} for s in self.students]
        ret['start_time'] = self.start_time
        ret['end_time'] = self.end_time
        return ret


class ScheduledClassesStudent(db.Model, SqlalchemySerializer):
    """
    ORM object for linking table between schedule classes and students

    This link means the student is a member of the scheduled class
    """
    __tablename__ = 'scheduled_classes_students'
    id = db.Column(db.Integer, primary_key=True)
    scheduled_class_id = db.Column(db.Integer, db.ForeignKey('scheduled_classes.id', ondelete="CASCADE"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete="CASCADE"), nullable=False)

    scheduled_class = db.relationship("ScheduledClass", back_populates="scheduled_classes_student")
    student = db.relationship("Student", back_populates="scheduled_classes_student")

    def __str__(self):
        return "{} {}".format(self.scheduled_class, self.student)


class Notification(db.Model, SqlalchemySerializer):
    """
    ORM object representing a single notifications.

    Notifications can be used to report info back to the user including warnings and errors
    """
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(40), nullable=False) # success, info, warning, error
    subject = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    unread = db.Column(db.Boolean, nullable=False, default=True)
