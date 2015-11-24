import logging
from flask import Blueprint
from flask.ext.jwt import current_identity
from schoolbloc import auth_required
from schoolbloc.users.models import User, UserError, RoleError
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
        return user.jsonify()

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
        parser.add_argument('role')

        # Parse data from incoming request
        args = parser.parse_args()
        username = args.get('username')
        password = args.get('password')
        role_name = args.get('role')

        # Update user information
        user = get_user_or_abort(user_id)
        try:
            if username:
                user.update_username(username)
            if password:
                user.update_password(password)
            if role_name:
                user.update_role(role_name)
        except UserError:
            abort(409, message="A user with that name already exists")
        except RoleError:
            abort(404, message="Role not found")

        # TODO find out what ryan wants for successful return data here
        return {'success': 'user updated successfully'}, 200

    @auth_required(roles=['admin'])
    def delete(self, user_id):
        """ Delete an existing User (admins only) """
        user = get_user_or_abort(user_id)
        user.delete()


class UserListApi(Resource):
    """ Get all users or create new user """
    @auth_required(roles=['teacher', 'admin'])
    def get(self):
        """ Get a list of users """
        return [user.jsonify for user in User.query.all()]

    @auth_required()
    def post(self):
        """ Create a new user """
        try:
            pass  # get args (either parser or wtforms) and attempt to create user
        except UserError:
            return {'error': 'The user already exists in the database'}, 409


api.add_resource(UserApi, '/api/users/<int:user_id>')
api.add_resource(UserListApi, '/api/users')
