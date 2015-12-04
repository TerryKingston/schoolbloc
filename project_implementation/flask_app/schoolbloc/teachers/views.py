import logging
from flask import Blueprint
from sqlalchemy.exc import IntegrityError

from schoolbloc import auth_required, db, User
from schoolbloc.teachers.models import Teacher
from flask.ext.restful import Api, Resource, abort, reqparse

# Setup logger
log = logging.getLogger(__name__)

# Blueprint and restful settings
mod = Blueprint('teacher', __name__)
api = Api(mod)


def get_teacher_or_abort(teacher_id):
    # If the user doesn't exist, abort
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        abort(404, message="teacher {} doesn't exist".format(teacher_id))
    return teacher


class TeacherApi(Resource):

    @auth_required(roles='admin')
    def get(self, teacher_id):
        teacher = get_teacher_or_abort(teacher_id)
        return teacher.serialize()

    @auth_required(roles='admin')
    def put(self, teacher_id):
        # Optional data
        parser = reqparse.RequestParser()
        parser.add_argument('first_name')
        parser.add_argument('last_name')

        # Parse data from incoming request
        args = parser.parse_args()
        first_name = args.get('first_name')
        last_name = args.get('last_name')

        # Update user information and save it to the db. Don't commit the changes
        # until the end, so that if one thing fails this entire request fails
        teacher = get_teacher_or_abort(teacher_id)
        if first_name:
            teacher.first_name = first_name
        if last_name:
            teacher.last_name = last_name
        db.session.add(teacher)
        db.session.commit()
        return {'success': 'teacher updated successfully'}, 200

    @auth_required(roles='admin')
    def delete(self, teacher_id):
        """ Delete an existing User (admins only) """
        teacher = get_teacher_or_abort(teacher_id)
        db.session.delete(teacher)
        db.session.commit()
        return {'success': 'teacher deleted successfully'}, 200


class TeacherListApi(Resource):
    """ Get all users or create new user """

    @auth_required(roles=['admin'])
    def get(self):
        return [teacher.serialize() for teacher in teacher.query.all()]

    @auth_required(roles='admin')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('first_name', required=True)
        parser.add_argument('last_name', required=True)
        args = parser.parse_args()
        try:
            u = User(username=args['username'], password=args['password'], role_type='teacher')
            s = Teacher(first_name=args['first_name'], last_name=args['last_name'], user_id=u.id)
            db.session.add(u)
            db.session.add(s)
            db.session.commit()
        except IntegrityError:
            db.session.rollbacke()
            return {'error': 'unique constraint failed'}, 409
        return {'success': 'teacher created successfully'}, 200

api.add_resource(TeacherApi, '/api/teachers/<int:teacher_id>')
api.add_resource(TeacherListApi, '/api/teachers')
