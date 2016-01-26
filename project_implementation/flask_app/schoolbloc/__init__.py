from functools import wraps
import logging
from flask import Flask, current_app
from flask.ext.jwt import current_identity, JWT, _jwt_required
from flask.ext.restful import abort
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound


# Create a logger to be used
log = logging.getLogger(__name__)

# Create the flask application
app = Flask(__name__)
app.config.from_object('config')

# Create the sqlalchemy database object. The actual database configuration is
# defined in config.py so we can swap between dev and production with only
# having to change that one file
db = SQLAlchemy(app)


# Have to import this after db and app have been declared
from schoolbloc.users.models import User, InvalidPasswordError


def authenticate(username, password):
    """ Login handler for javascript web token """
    try:
        user = User.query.filter_by(username=username).one()
        user.verify_password(password)
        return user
    except (NoResultFound, InvalidPasswordError):
        return None


def identity(payload):
    """ Given the jwt payload, return the authenticated user (or None) """
    user_id = payload['identity']
    return User.query.get(user_id)


# Create the javascript web tokens auth engine
jwt = JWT(app, authenticate, identity)


def auth_required(realm=None, roles=None):
    """
    I had to do some hacking to get this working, as it was complainging about
    not being in a context if I tried to chain the jwt_required() decorator
    together with this role based decorator. The end result is this, which just
    takes the jwt_required decorator, and append my custom role stuff to the
    end of it. This works fine, but it does mean that if flask-jwt gets updated
    this may need to change to match.
    """
    # TODO look into this more and see if I can get this working with chaining
    #      decorators. Will be better for dependencies in the long run
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # The jwt_required decorator functionality
            _jwt_required(realm or current_app.config['JWT_DEFAULT_REALM'])

            # Verify this user has the correct role
            current_user_role = current_identity.role.role_type
            authorized = False
            if not roles:
                authorized = True
            elif isinstance(roles, str):
                if current_user_role.lower() == roles.lower():
                    authorized = True
            elif isinstance(roles, list):
                if current_user_role.lower() in [r.lower() for r in roles]:
                    authorized = True

            if not authorized:
                abort(403, message="Permission denied")
            return fn(*args, **kwargs)
        return decorator
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
from schoolbloc.data_import.views import mod as data_import_mod
from schoolbloc.scheduler.views import mod as scheduler_mod
from schoolbloc.users.views import mod as users_mod
app.register_blueprint(data_import_mod)
app.register_blueprint(scheduler_mod)
app.register_blueprint(users_mod)
