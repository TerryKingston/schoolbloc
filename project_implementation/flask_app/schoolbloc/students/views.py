import logging
from flask import Blueprint
from flask.ext.jwt import current_identity
from sqlalchemy.exc import IntegrityError

from schoolbloc import auth_required, db, User
from schoolbloc.students.models import Student, StudentGroup
from flask.ext.restful import Api, Resource, abort, reqparse

# Setup logger
log = logging.getLogger(__name__)

# Blueprint and restful settings
mod = Blueprint('students', __name__)
api = Api(mod)


def get_student_or_abort(student_id):
    """
    Returns a user object if the user exist and the caller has permission
    to get this information. Aborts with a 404 otherwise
    """
    # If the user doesn't exist, abort
    student = Student.query.get(student_id)
    if not student:
        abort(404, message="student {} doesn't exist".format(student_id))

    # If this is a student, don't give him/her access to other students info.
    # Return the same 404 error so they can't find other valid user ids either
    if current_identity.role.role_type == 'student':
        if current_identity.id != student_id:
            abort(404, message="user {} doesn't exist".format(student_id))
    return student


class StudentApi(Resource):
    """ Get/modify/delete a specific user """

    @auth_required()
    def get(self, student_id):
        """ Get info on a User """
        student = get_student_or_abort(student_id)
        return student.jsonify()

    @auth_required(roles='admin')
    def put(self, student_id):
        """
        Update settings of a User (password, address, email, etc)

        Any user can update their own settings, and admins can update any users
        settings
        """
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
        student = get_student_or_abort(student_id)
        if first_name:
            student.first_name = first_name
        if last_name:
            student.last_name = last_name
        db.session.add(student)
        db.session.commit()

        return {'success': 'user updated successfully'}, 200

    @auth_required(roles='admin')
    def delete(self, student_id):
        """ Delete an existing User (admins only) """
        student = get_student_or_abort(student_id)
        db.session.delete(student)
        db.session.commit()
        return {'success': 'user deleted successfully'}, 200


class StudentListApi(Resource):
    """ Get all users or create new user """

    @auth_required(roles=['teacher', 'admin'])
    def get(self):
        """ Get a list of students """
        return [student.jsonify() for student in Student.query.all()]

    @auth_required(roles='admin')
    def post(self):
        """ Create a new user """
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('first_name', required=True)
        parser.add_argument('last_name', required=True)
        args = parser.parse_args()
        try:
            u = User(username=args['username'], password=args['password'], role_type='student')
            s = Student(first_name=args['first_name'], last_name=args['last_name'], user_id=u.id)
            db.session.add(u)
            db.session.add(s)
            db.session.commit()
        except IntegrityError:
            db.session.rollbacke()
            return {'error': 'unique constraint failed'}, 409

        return {'success': 'Student created successfully'}, 200

api.add_resource(StudentApi, '/api/students/<int:student_id>')
api.add_resource(StudentListApi, '/api/students/')
