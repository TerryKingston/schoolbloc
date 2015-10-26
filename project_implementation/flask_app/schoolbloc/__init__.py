from functools import wraps
import logging
from flask import Flask, url_for, redirect
from flask.ext.jwt import jwt_required, current_identity, JWT
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

from schoolbloc.login.models import User


# Create a logger to be used
log = logging.getLogger(__name__)

# Create the flask application
app = Flask(__name__)
app.config.from_object('config')

# Create the sqlalchemy database object. The actual database configuration is
# defined in config.py so we can swap between dev and production with only
# having to change that one file
db = SQLAlchemy(app)


# Create the javascript web tokens auth engine
jwt = JWT(app)


@jwt.authentication_handler
def authenticate(username, password):
    """ Login handler for javascript web token """
    try:
        user = User.query.filter_by(username=username).one()
        if user.verify_password(password):
            return user
        else:
            return None
    except NoResultFound:
        return None


@jwt.identity_handler
def identity(payload):
    """ Given the jwt payload, return the authenticated user (or None) """
    user_id = payload['identity']
    return User.get(user_id)


@jwt_required()
def auth_required(func, roles=None):
    """
    Decorator that protects restful endpoints based on roles. By default, any
    user with authorization (a jwt) can access a protected endpoint, but you
    can change this behavior with the roles key word argument. This can be
    a single string (which matches the Roles.role_type string in the database),
    or a list of roles which can be any number of roles in the database.

    Ex:
    @auth_required()
    def foo():
        ...

    @auth_required(roles='students')
    def foo2():
        ...

    @auth_required(roles=['teachers', 'admins'])
    def foo3():
        ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get role of current user. Raise exception if they don't have a jwt
        current_user_role = current_identity.role.role_type

        authorized = False
        if not roles:
            authorized = True
        elif isinstance(roles, str):
            if current_user_role.lower() == roles.lower():
                authorized = True
        elif isinstance(roles, list):
            if current_user_role.lower() in roles:
                authorized = True

        if authorized:
            return func(*args, **kwargs)
        else:
            return 'fail'  # TODO Use the results from flask-jwt
    return wrapper


# We can set 404 or 408 error pages here, but perhaps that should be handled by
# angular instead? (at least the 404). TODO
@app.errorhandler(404)
def page_not_found(e):
    return '404 page not found'


@app.errorhandler(408)
def page_not_found(e):
    return '408 request timed out'


# Import blueprints
# This is where we take our backend modules (they are modules for the sake of
# code organization, not models that can be toggled like the frontend angular
# modules). All of our code will be in the modules
from schoolbloc.blueprint.views import mod as blueprint_module
from schoolbloc.login.views import mod as login_module
app.register_blueprint(blueprint_module)
app.register_blueprint(login_module)
