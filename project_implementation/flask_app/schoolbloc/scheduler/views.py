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

    @auth_required(roles='admin')
    def get(self):
        notes = Notification.query.filter_by(unread=True).all()
        for note in notes:
            note.unread = False
            db.session.add(note)
        db.session.commit()
        return [note.serialize() for note in notes]


class ScheduleApi(Resource):

    @auth_required(roles='admin')
    def get(self, schedule_id):
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            abort(404, message="Schedule {} not found".format(schedule_id))
        return schedule.serialize(expanded=True)

    @auth_required(roles='admin')
    def delete(self, schedule_id):
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            abort(404, message="Schedule {} not found".format(schedule_id))
        db.session.delete(schedule)
        db.session.commit()
        return {'success': True}


class ScheduleStudentApi(Resource):

    @auth_required(roles='admin')
    def get(self, schedule_id):
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            abort(404, message="Schedule {} not found".format(schedule_id))
        return schedule.student_serialize()

    @auth_required(roles='admin')
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

    @auth_required(roles='admin')
    def get(self):
        schedules = Schedule.query.all()
        return [s.serialize(expanded=False) for s in schedules]

    @auth_required(roles='admin')
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
        if 'user_token' not in request_json:
            abort(400, message='missing access token in request')

        try:
            student = Student.query.filter_by(user_token=request_json['user_token']).one()
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

    def _get_all_student_courses(self, student_id):
        courses = {}

        # Get courses from subjects that this student belongs to
        for ss in StudentsSubject.query.filter_by(student_id=student_id).all():
            for course_sub in CoursesSubject.query.filter_by(subject_id=ss.subject_id).all():
                if course_sub.course_id not in courses:
                    courses[course_sub.course_id] = {
                        'priority': course_sub.priority,
                        'rank': 0,
                    }
                else:
                    current_priority = courses[course_sub.course_id]['priority']
                    if self._greater_priority(course_sub.priority, current_priority):
                        courses[course_sub.course_id]['priority'] = course_sub.priority

        # Get courses from student groups that this student belongs to
        for ssg in StudentsStudentGroup.query.filter_by(student_id=student_id).all():

            # Get via subjects
            for sgs in StudentGroupsSubject.query.filter_by(student_group_id=ssg.student_group_id).all():
                for course_sub in CoursesSubject.query.filter_by(subject_id=sgs.subject_id).all():
                    if course_sub.course_id not in courses:
                        courses[course_sub.course_id] = {
                            'priority': course_sub.priority,
                            'rank': 0,
                        }
                    else:
                        current_priority = courses[course_sub.course_id]['priority']
                        if self._greater_priority(course_sub.priority, current_priority):
                            courses[course_sub.course_id]['priority'] = course_sub.priority

            # Get via courses
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
                courses[cs.course_id]['rank'] = cs.rank  # guaranteed to be >=
                current_priority = courses[cs.course_id]['priority']
                if self._greater_priority(cs.priority, current_priority):
                    courses[cs.course_id]['priority'] = cs.priority

        return courses

    @staticmethod
    def _get_student_id_or_abort():
        """
        Return the student id, assuming it exists and that this user has
        access to do stuff on this student id
        """
        role = current_identity.role.role_type
        current_user_id = current_identity.id

        # First, make sure the student id exists, either in the request, or
        # as it is a student who logged on
        student_id = request.args.get('user_id')
        if student_id:
            try:
                student_id = int(student_id)
            except ValueError:
                abort(400, message="user_id must be an integer")
        else:
            if role == 'student':
                student = Student.query.filter_by(user_id=current_user_id).one()
                student_id = student.id
            else:
                abort(400, message="Missing parameter 'user_id'")

        # Next, see if this user has permission to access this student id. Admins
        # can access any student ids, parents can access their students, and
        # students can only access themselves
        if role == 'admin':
            return
        elif role == 'student':
            student = Student.query.filter_by(id=student_id).one()
            if student.user_id != current_user_id:
                abort(404, message='Access denied')
        elif role == 'parent':
            parent = Parent.query.filter_by(user_id=current_identity.id).one()
            found = False
            for student in parent.students:
                if student.id == student_id:
                    found = True
                    break
            if not found:
                abort(404, message='Access denied')
        else:
            abort(404, message='Expect role of admin, student or teacher')

        return student_id

    @auth_required(roles=['student', 'parent', 'admin'])
    def get(self):
        electives = request.args.get('electives')
        student_id = self._get_student_id_or_abort()
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
            if priority == 'mandatory':
                abort(400, message='cannot set priority to mandatory')
        except KeyError:
            abort(400, message='missing id, rank, or priority in request')
        student_id = self._get_student_id_or_abort()

        # If we already have an existing CourseStudnet constraint for this, just
        # update this
        cs = CoursesStudent.query.filter_by(course_id=course_id,
                                            student_id=student_id).first()
        if cs:
            if cs.priority == "mandatory":
                abort(400, message="Cannot lower priority of a mandatory course")
            cs.priority = priority
            cs.rank = rank
            db.session.add(cs)
            db.session.commit()
            return {'success': True}

        # Otherwise, verify that this student has this course in one of this
        # student groups, and add the constraint to the
        avail_student_courses = self._get_all_student_courses(student_id)
        if request_json['id'] not in avail_student_courses:
            abort(400, message="No mapping exists between this student and course")

        cs = CoursesStudent(active=True, priority=priority, rank=rank,
                            course_id=course_id, student_id=student_id)
        db.session.add(cs)
        db.session.commit()
        return {'success': True}

    @auth_required(roles=['student', 'parent', 'admin'])
    def put(self):
        student_id = self._get_student_id_or_abort()
        request_json = request.get_json(force=True)
        for data in request_json:
            if "id" not in data or "rank" not in data:
                db.session.rollback()
                abort(400, message="Missing id or rank in json dict")
            try:
                cs = CoursesStudent.query.filter_by(course_id=data['id'],
                                                    student_id=student_id).one()
                if cs.priority == "mandatory":
                    abort(400, message="Cannot change rank of a mandatory course")
                cs.rank = data['rank']
                db.session.add(cs)
            except NoResultFound:
                db.session.rollback()
                abort(400, message="CourseStudent mapper not found")
        db.session.commit()
        return {'success': True}

    @auth_required(roles=['student', 'parent', 'admin'])
    def delete(self):
        student_id = self._get_student_id_or_abort()
        course_id = request.args.get('course_id')
        if not course_id:
            abort(400, message="Missing course_id in url params")
        try:
            course_id = int(course_id)
        except ValueError:
            abort(400, message="course_id must be an integers")

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
