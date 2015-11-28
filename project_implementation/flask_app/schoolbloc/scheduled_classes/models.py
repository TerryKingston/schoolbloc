import logging
from schoolbloc import db
from sqlalchemy.exc import IntegrityError
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

    def __init__(self, course_id, classroom_id, teacher_id, start_time, end_time):
        
        self.course_id = course_id
        self.classroom_id = classroom_id
        self.teacher_id = teacher_id
        
        # the ids could be invalid
        try:
            db.session.add(self)
            db.session.commit()
            log.info('added new ScheduledCourse: course={} classroom={} teacher={}'.format(
                course_id, classroom_id, teacher_id))
        except IntegrityError as e:
            raise ScheduledClassError(e.statement)

    def __repr__(self):
        return "<course_id={} teacher_id={} classroom_id={}>".format(
            self.course_id, self.teacher_id, self.classroom_id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class ScheduledClassesStudentError(Exception):
    pass

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

    def __init__(self, scheduled_class_id, student_id, active=True):

        self.scheduled_class_id = scheduled_class_id
        self.student_id = student_id
        self.active = active
        
        # the ids could be invalid
        try:
            db.session.add(self)
            db.session.commit()
            log.info("added new ScheduledClassesStudent: student_id={} scheduled_class_id={}".format(
                student_id, scheduled_class_id ))
        
        except IntegrityError as e:
            raise ScheduledClassesStudentError(e.statement)

    def __repr__(self):
        return "<scheduled_class_id={} student_id={}>".format(self.scheduled_class_id, self.student_id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()