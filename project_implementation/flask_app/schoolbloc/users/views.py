import logging
from flask import Blueprint, request, current_app
from flask.ext.jwt import current_identity
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.local import LocalProxy

from schoolbloc import auth_required, db
from schoolbloc.scheduler.models import Student, Parent
from schoolbloc.users.models import User
from flask.ext.restful import Api, Resource, abort, reqparse

# Setup logger
log = logging.getLogger(__name__)

# Blueprint and restful settings
mod = Blueprint('user', __name__)
api = Api(mod)


def get_user_or_abort(user_id):
    """
    Returns a user object if the user exist and the caller has permission
    to get this information. Aborts with a 404 otherwise
    """
    # If the user doesn't exist, abort
    user = User.query.get(user_id)
    if not user:
        abort(404, message="user {} doesn't exist".format(user_id))

    # If this is a student, don't give him/her access to other students info.
    # Return the same 404 error so they can't find other valid user ids either
    if current_identity.role.role_type == 'student':
        if current_identity.id != user_id:
            abort(404, message="user {} doesn't exist".format(user_id))

    return user


class UserApi(Resource):
    """ Get/modify/delete a specific user """

    @auth_required()
    def get(self, user_id):
        """ Get info on a User """
        user = get_user_or_abort(user_id)
        return user.serialize()

    @auth_required()
    def put(self, user_id):
        """
        Update settings of a User (password, address, email, etc)

        Any user can update their own settings, and admins can update any users
        settings
        """
        # Optional data
        parser = reqparse.RequestParser()
        parser.add_argument('username')
        parser.add_argument('password')

        # Parse data from incoming request
        args = parser.parse_args()
        username = args.get('username')
        password = args.get('password')

        # Update user information and save it to the db. Don't commit the changes
        # until the end, so that if one thing fails this entire request fails
        user = get_user_or_abort(user_id)
        try:
            if username:
                if user.role.role_type == 'student':
                    abort(403, message='Students cannot update username')
                else:
                    user.username = username
            if password:
                user.update_password(password)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(409, message="Duplicate username")
        return {'success': 'user updated successfully'}, 200

    @auth_required(roles=['admin'])
    def delete(self, user_id):
        """ Delete an existing User (admins only) """
        user = get_user_or_abort(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'success': 'user deleted successfully'}, 200


class UserListApi(Resource):
    """ Get all users or create new user """

    @auth_required(roles='admin')
    def get(self):
        """ Get a list of users """
        return [user.serialize() for user in User.query.all()]


class UserRegister(Resource):

    def post(self):
        """ Create a new user """
        request_json = request.get_json(force=True)

        # Required args for all users
        try:
            username = request_json['username']
            password = request_json['password']
            role_type = request_json['role_type']
        except KeyError as e:
            abort(400, message="Missing required key: {}".format(e))

        # If it's a student
        if role_type == 'student':
            try:
                user_token = request_json['user_token']
            except KeyError as e:
                abort(400, message="Student missing required key: {}".format(e))

            try:
                student = Student.query.filter_by(user_token=user_token).one()
                existing_user = User.query.filter_by(id=student.user_id).first()
                if existing_user:
                    abort(400, message="This student already belongs to a user")
                user = User(username, password, role_type)
                db.session.add(user)
                db.session.flush()
                student.user_id = user.id
                db.session.add(student)
                db.session.commit()

                # Log the user in
                _jwt = LocalProxy(lambda: current_app.extensions['jwt'])
                identity = _jwt.authentication_callback(username, password)
                access_token = _jwt.jwt_encode_callback(identity)
                return _jwt.auth_response_callback(access_token, identity)
            except NoResultFound:
                abort(400, message="student user token not found")
            except IntegrityError:
                db.session.rollback()
                abort(400, message="Username already exists")

        # Add if it's a parent
        elif role_type == 'parent':
            try:
                first_name = request_json['first_name']
                last_name = request_json['last_name']
                email = request_json['email']
            except KeyError as e:
                abort(400, message="Parent missing required key: {}".format(e))

            try:
                user = User(username, password, role_type)
                db.session.add(user)
                db.session.flush()
                parent = Parent(user_id=user.id, first_name=first_name,
                                last_name=last_name, email=email)
                db.session.add(parent)
                db.session.commit()

                # Log the user in
                _jwt = LocalProxy(lambda: current_app.extensions['jwt'])
                identity = _jwt.authentication_callback(username, password)
                access_token = _jwt.jwt_encode_callback(identity)
                return _jwt.auth_response_callback(access_token, identity)
            except IntegrityError:
                db.session.rollback()
                abort(400, message="Username already exists")

        else:
            abort(400, message="Role type must be parent or student")


api.add_resource(UserApi, '/api/users/<int:user_id>')
api.add_resource(UserListApi, '/api/users')
api.add_resource(UserRegister, '/api/register')
