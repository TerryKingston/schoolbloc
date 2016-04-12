from threading import Thread

from flask import Blueprint, request
from flask.ext.jwt import current_identity
from flask.ext.restful import Api, Resource, abort
from sqlalchemy.orm.exc import NoResultFound

from schoolbloc import auth_required
from schoolbloc.scheduler.restexport import TestRest, TestRestList
from schoolbloc.scheduler.models import *
from schoolbloc.scheduler.scheduler import Scheduler, SchedulerNoSolution

mod = Blueprint('api', __name__)
api = Api(mod)


def register_rest_orm(orm, get='admin', put='admin', post='admin',
                      delete='admin', list='admin'):
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


# TODO incorporate parents into this
def student_parent_get_or_abort(self, orm_id):
    orm_object = self.orm.query.get(orm_id)
    if not orm_object:
        abort(404, message="ID {} not found".format(orm_id))
    if current_identity.role.role_type in ('student', 'parent'):
        if current_identity.id != orm_object.user_id:
            abort(404, message='Denied')
    return orm_object


# Expose facts and constraints over rest api
register_rest_orm(Course)
register_rest_orm(CoursesStudent)
register_rest_orm(CoursesTeacher)
register_rest_orm(CoursesStudentGroup)
register_rest_orm(CoursesSubject)
register_rest_orm(Classroom)
register_rest_orm(ClassroomsTeacher)
register_rest_orm(ClassroomsCourse)
register_rest_orm(Day)
register_rest_orm(StudentGroup)
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
register_rest_orm(Notification)

# TODO probably don't want to let students modify everything of their own. Figure
#      out the specs, and override something to studnets can only hvae limited perms
s_cls, sl_cls = register_rest_orm(Student, get=None, put=['student', 'parent', 'admin'])
s_cls._get_or_abort = student_parent_get_or_abort
sl_cls._get_or_abort = student_parent_get_or_abort


# Additional rest apis we are exposing
class UnreadNotifications(Resource):

    def get(self):
        notes = Notification.query.filter_by(unread=True).all()
        for note in notes:
            note.unread = False
            db.session.add(note)
        db.session.commit()
        return [note.serialize() for note in notes]


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


class ScheduleStudentApi(Resource):

    def get(self, schedule_id):
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            abort(404, message="Schedule {} not found".format(schedule_id))
        return schedule.student_serialize()

    def delete(self, schedule_id):
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            abort(404, message="Schedule {} not found".format(schedule_id))
        db.session.delete(schedule)
        db.session.commit()
        return {'success': True}


class CreateSchedule(Thread):

    def run(self):
        scheduler = Scheduler()
        scheduler.make_schedule()


class ScheduleListApi(Resource):

    def get(self):
        schedules = Schedule.query.all()
        return [s.serialize(expanded=False) for s in schedules]

    def post(self):
        worker_thread = CreateSchedule()
        worker_thread.daemon = True
        worker_thread.start()
        return {'success': 'Started generating schedule'}


class ParentsStudents(Resource):

    @auth_required(roles='parent')
    def get(self):
        try:
            parent = Parent.query.filter_by(user_id=current_identity.id).one()
        except NoResultFound:
            return []
        return [s.serialize() for s in parent.students]

    @auth_required(roles='parent')
    def post(self):
        request_json = request.get_json(force=True)
        if 'access_token' not in request_json:
            abort(400, message='missing access token in request')

        try:
            student = Student.query.filter_by(access_token=request_json['access_token']).one()
        except NoResultFound:
            abort(400, message='Student with requested user token not found')

        parent = Parent.query.filter_by(user_id=current_identity.id).one()
        db.session.add(ParentStudentMapper(parent_id=parent.id, student_id=student.id))
        db.session.commit()
        return student.serialize()


class StudentCourseSelector(Resource):

    @staticmethod
    def _greater_priority(p1, p2):
        """ Compares if p1 > p2 """
        # Cannot be lower then low or higher then mandatory, so we only have
        # to check the 'high' case
        if p1 == 'high':
            if p2 == 'low':
                return True
        return False

    @staticmethod
    def _course_student_mapper_exists(course_id, student_id):
        for ssg in StudentsStudentGroup.query.filter_by(student_id=student_id).all():
            for csg in CoursesStudentGroup.query.filter_by(student_group_id=ssg.student_group_id).all():
                if course_id == csg.course_id:
                    return True
        return False

    def _get_all_student_courses(self, student_id):
        # Get the student groups ones first, as they may be overwritten by
        # student courses.
        courses = {}
        for ssg in StudentsStudentGroup.query.filter_by(student_id=student_id).all():
            for csg in CoursesStudentGroup.query.filter_by(student_group_id=ssg.student_group_id).all():
                if csg.course_id not in courses:
                    courses[csg.course_id] = {
                        'priority': csg.priority,
                        'rank': 0,
                    }
                else:
                    current_priority = courses[csg.course_id]['priority']
                    if self._greater_priority(csg.priority, current_priority):
                        courses[csg.course_id]['priority'] = csg.priority

        # Now handle the individual overrides that can happen in CoursesStudent
        for cs in CoursesStudent.query.filter_by(student_id=student_id).all():
            if cs.course_id not in courses:
                courses[cs.course_id] = {
                    'priority': cs.priority,
                    'rank': cs.rank,
                }
            else:
                courses[csg.course_id]['rank'] = cs.rank  # guaranteed to be >=
                current_priority = courses[cs.course_id]['priority']
                if self._greater_priority(cs.priority, current_priority):
                    courses[csg.course_id]['priority'] = cs.priority
        return courses

    @staticmethod
    def _verify_access_or_abort(student_id):
        """ Don't let students or parents access other students data """
        role = current_identity.role.role_type
        current_user_id = current_identity.id

        # admins can access anyone
        if role == 'admin':
            return

        # students can only access themselves
        elif role == 'student':
            student = Student.query.filter_by(id=student_id).one()
            if student.user_id != current_user_id:
                abort(404, message='Access denied')

        # parents can access any of their students
        elif role == 'parent':
            parent = Parent.query.filter_by(user_id=current_identity.id).one()
            for student in parent.students:
                if student.id == student_id:
                    return
            abort(404, message='Access denied')

        else:
            abort(404, message='Expect role of admin, student or teacher')

    @auth_required(roles=['student', 'parent', 'admin'])
    def get(self):
        electives = request.args.get('electives')
        student_id = request.args.get('user_id')
        if not student_id:
            abort(400, message="Missing user_id in url params")
        try:
            student_id = int(student_id)
        except ValueError:
            abort(400, message="user_id must be an integer")
        self._verify_access_or_abort(student_id)

        courses = self._get_all_student_courses(student_id)

        ret = []
        if electives and electives.lower() == 'true':
            for course_id, course_dict in courses.items():
                if course_dict['priority'] == 'low':
                    c = Course.query.filter_by(id=course_id).one()
                    ret.append({
                        'id': c.id,
                        'course': str(c),
                    })
        else:
            for course_id, course_dict in courses.items():
                if course_dict['priority'] != 'low':
                    c = Course.query.filter_by(id=course_id).one()
                    ret.append({
                        'id': c.id,
                        'course': str(c),
                        'priority': course_dict['priority'],
                        'rank': course_dict['rank'],
                    })
        return ret

    @auth_required(roles=['student', 'parent', 'admin'])
    def post(self):
        request_json = request.get_json(force=True)
        try:
            course_id = request_json['id']
            priority = request_json['priority']
            rank = request_json['rank']
        except KeyError:
            abort(400, message='missing id, rank, or priority in request')

        if priority == 'mandatory':
            abort(400, message='cannot set priority to mandatory')

        student_id = request.args.get('user_id')
        if not student_id:
            abort(400, message="Missing user_id in url params")
        try:
            student_id = int(student_id)
        except ValueError:
            abort(400, message="user_id must be an integer")

        try:
            student = Student.query.filter_by(id=student_id).one()
        except NoResultFound:
            abort(400, message="Student ID {} not found".format(student_id))

        self._verify_access_or_abort(student.id)

        # If we already have an existing CourseStudnet constraint for this, just
        # update this
        cs = CoursesStudent.query.filter_by(course_id=course_id,
                                            student_id=student.id).first()
        if cs:
            if cs.priority == "mandatory":
                abort(400, message="Cannot lower priority of a mandatory course")
            cs.priority = priority
            cs.rank = rank
            db.session.add(cs)
            db.session.commit()
            return {'success': True}

        # Otherwise, verify that this student has this course in one of this
        # studnet groups, and add the constraint to the
        if not self._course_student_mapper_exists(request_json['id'], student.id):
            abort(400, message="No mapping exists between this student and course")

        cs = CoursesStudent(active=True, priority=priority, rank=rank,
                            course_id=course_id, student_id=student.id)
        db.session.add(cs)
        db.session.commit()
        return {'success': True}

    @auth_required(roles=['student', 'parent', 'admin'])
    def delete(self):
        student_id = request.args.get('user_id')
        course_id = request.args.get('course_id')
        if not student_id or not course_id:
            abort(400, message="Missing user_id in url params")
        try:
            student_id = int(student_id)
            course_id = int(course_id)
        except ValueError:
            abort(400, message="user_id and course_id must be an integers")

        self._verify_access_or_abort(student_id)
        cs = CoursesStudent.query.filter_by(course_id=course_id,
                                            student_id=student_id).first()
        cs.rank = 0
        cs.priority = 'low'
        db.session.add(cs)
        db.session.commit()
        return {'success': True}


api.add_resource(UnreadNotifications, '/api/notifications/unread')
api.add_resource(ScheduleApi, '/api/schedules/<int:schedule_id>/class')
api.add_resource(ScheduleStudentApi, '/api/schedules/<int:schedule_id>/student')
api.add_resource(ScheduleListApi, '/api/schedules')
api.add_resource(ParentsStudents, '/api/my_students')
api.add_resource(StudentCourseSelector, '/api/student_course')
