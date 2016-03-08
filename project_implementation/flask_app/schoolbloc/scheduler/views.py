from flask import Blueprint
from flask.ext.restful import Api, Resource, abort
from schoolbloc import auth_required
from schoolbloc.scheduler.restexport import TestRest, TestRestList
from schoolbloc.scheduler.models import *

mod = Blueprint('api', __name__)
api = Api(mod)


def register_rest_orm(orm, get=False, put='admin', post='admin',
                      delete=False, list=False):
    """
    Registar a sqlalchemy orm model to be exposed via the rest api. By default,
    only admins will be authorized to access each of the rest methods. You can override
    this by passing in a value to get, put, post, delete, and list to add different
    access controls to each individual method.

    The valid values you can pass to these are:
        - A string, which is the one role who can access this endpoint
        - A list, which is a list of roles (strings) who can access this endpoint
        - None, which is anyone with a valid JWT (login token) can access this endpoint
        - False, which is anyone can access this endpoint

    This returns the classes created for this rest endpoint (class for interacting
    with a specific object, and class_list for listing all objects and creating
    new ones), which lets you override specific functions if so desired.
    IE, if you want to use this, but want to override the POST method, you can
    call this method, then override the post method with cls.post = <a_different_method>.
    """
    # We are basing the endpoint name on the tablename for simplicity sake
    name = orm.__tablename__

    # Create the single object get/modify/delete endpoints, and apply access controls
    cls = type(name, (TestRest,), {'orm': orm})
    if get is not False:
        cls.get = auth_required(roles=get)(cls.get)
    if put is not False:
        cls.put = auth_required(roles=put)(cls.put)
    if delete is not False:
        cls.delete = auth_required(roles=delete)(cls.delete)

    # Create list/post endpoint, and apply access control decorators if present
    cls_list = type(name + 'list', (TestRestList,), {'orm': orm})
    if list is not False:
        cls_list.get = auth_required(roles=list)(cls_list.get)
    if post is not False:
        cls_list.post = auth_required(roles=post)(cls_list.post)

    # Register the classes to the rest api
    api.add_resource(cls, '/api/{}/<int:orm_id>'.format(name))
    api.add_resource(cls_list, '/api/{}'.format(name))

    # Return the classes, so that the caller can overwrite a function if desired
    return cls, cls_list


# Expose facts and constraints over rest api
register_rest_orm(Course)
register_rest_orm(CoursesStudent)
register_rest_orm(CoursesTeacher)
register_rest_orm(CoursesStudentGroup)
register_rest_orm(CoursesSubject)
register_rest_orm(Classroom)
register_rest_orm(ClassroomsTeacher)
register_rest_orm(ClassroomsCourse)
register_rest_orm(StudentGroup)
register_rest_orm(Student)
register_rest_orm(StudentsStudentGroup)
register_rest_orm(StudentGroupsSubject)
register_rest_orm(StudentsSubject)
register_rest_orm(Subject)
register_rest_orm(Teacher)
register_rest_orm(CoursesTimeblock)
register_rest_orm(ClassroomsTimeblock)
register_rest_orm(StudentGroupsTimeblock)
register_rest_orm(StudentsTimeblock)
register_rest_orm(SubjectsTimeblock)
register_rest_orm(TeachersTimeblock)
register_rest_orm(Timeblock)


# Rest api for full schedules
class ScheduleApi(Resource):

    def get(self, schedule_id):
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            abort(404, message="Schedule {} not found".format(schedule_id))
        return schedule.serialize(expanded=True)

    def delete(self, schedule_id):
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            abort(404, message="Schedule {} not found".format(schedule_id))
        db.session.delete(schedule)
        db.session.commit()
        return {'success': True}


class ScheduleListApi(Resource):

    def get(self):
        schedules = Schedule.query.all()
        return [s.serialize(expanded=False) for s in schedules]

    def post(self):
        # TODO this is what calls into terrys code
        return {'success', True}

api.add_resource(ScheduleApi, '/api/schedules/<int:schedule_id>')
api.add_resource(ScheduleListApi, '/api/schedules')
