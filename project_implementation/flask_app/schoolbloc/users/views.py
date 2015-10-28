import logging
from flask import Blueprint
from flask.ext.jwt import current_identity
from schoolbloc import auth_required
from schoolbloc.users.models import User, UserError
from flask.ext.restful import Api, Resource, abort

# Setup logger
log = logging.getLogger(__name__)

# Blueprint and restful settings
mod = Blueprint('user', __name__, template_folder='templates')
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
        # TODO create serialize method or see if sqlalchemy can automatically jsonify this
        user = get_user_or_abort(user_id)
        ret = {
            'id': user.id,
            'username': user.username,
            'role': user.role.role_type
        }
        return ret

    @auth_required()
    def put(self, user_id):
        """ Update settings of a User (password, address, email, etc) """
        user = get_user_or_abort(user_id)

    @auth_required(roles=['admin'])
    def delete(self, user_id):
        """ Delete an existing User """
        # TODO probably only let an admin delete users.
        # TODO don't actually delete the user, just mark it as disabled in the db?
        user = get_user_or_abort(user_id)


class UserListApi(Resource):
    """ Get all users or create new user """
    @auth_required(roles=['teacher', 'admin'])
    def get(self):
        """ Get a list of users """
        ret = {}
        users = User.query.all()
        print(users)
        for user in users:
            ret[user.id] = {
                'username': user.username,
                'role': user.role.role_type,
            }
        return ret

    @auth_required()
    def post(self):
        """ Create a new user """
        try:
            pass  # get args (either parser or wtforms) and attempt to create user
        except UserError:
            return {'error': 'The user already exists in the database'}, 409


api.add_resource(UserApi, '/api/users/<int:user_id>')
api.add_resource(UserListApi, '/api/users')
