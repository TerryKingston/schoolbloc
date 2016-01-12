from flask import Blueprint
from flask.ext.restful import Api
from schoolbloc.constraints.restthing import TestRest, TestRestList

from schoolbloc.constraints.models import CoursesStudent, Course, \
    Teacher, Subject, StudentsStudentGroup, Student, StudentGroup, \
    ScheduledClassesStudent, ScheduledClass, Schedule, ClassroomsCourse, \
    ClassroomsTeacher, Classroom, CoursesSubject, CoursesStudentGroup, \
    CoursesTeacher

mod = Blueprint('api', __name__)
api = Api(mod)


def register_rest_orm(orm):
    name = orm.__tablename__
    cls = type(name, (TestRest,), {'orm': orm})
    api.add_resource(cls, '/api/{}/<int:orm_id>'.format(name))

    cls_list = type(name + 'list', (TestRestList,), {'orm': orm})
    api.add_resource(cls_list, '/api/{}'.format(name))

register_rest_orm(Course)
register_rest_orm(CoursesStudent)
register_rest_orm(CoursesTeacher)
register_rest_orm(CoursesStudentGroup)
register_rest_orm(CoursesSubject)
register_rest_orm(Classroom)
register_rest_orm(ClassroomsTeacher)
register_rest_orm(ClassroomsCourse)
register_rest_orm(Schedule)
register_rest_orm(ScheduledClass)
register_rest_orm(ScheduledClassesStudent)
register_rest_orm(StudentGroup)
register_rest_orm(Student)
register_rest_orm(StudentsStudentGroup)
register_rest_orm(Subject)
register_rest_orm(Teacher)
