import logging
from flask import Blueprint
from flask.ext.login import LoginManager, login_user, current_user, logout_user
from sqlalchemy.orm.exc import NoResultFound
from schoolbloc.login.forms import LoginForm
from schoolbloc.login.models import User, UserError
from flask.ext.restful import Api, Resource

# Setup logger
log = logging.getLogger(__name__)

# Blueprint and restful settings
mod = Blueprint('login', __name__, template_folder='templates')
api = Api(mod)

# Setup login manager
login_manager = LoginManager()


@mod.record_once
def on_load(state):
    """ Setup login manager when this blueprint is registered """
    login_manager.init_app(state.app)
    login_manager.login_view = "login.login"


@login_manager.user_loader
def load_user(user_id):
    """ Method code to reload a logged in user when a request comes in """
    return User.query.get(int(user_id))


# TODO this is untested and just thrown together. I haven't played with
# flask-restful in combination with flask-wtforms before, so we will see what
# happens (I'm guess some magic will be required for csrf protection).
# Also, this is not set it stone by any means, and we could use another
# system for managing logins if so desired
class Login(Resource):
    """ Restful API for logging in """
    # TODO: Should the get request return template html to angular.js, or should
    #       we disable get requests for this all together. Ask Ryan, guessing the later
    def post(self):
        """ Endpoint for logging in a user """
        form = LoginForm()
        if not form.validate_on_submit():
            return form.errors, 422

        try:
            user = User.query.filter_by(username=form.username.data).one()
            user.verify_password(form.password.data)
            login_user(user)
            return {'success': 'User logged in successfully'}, 200
        except (NoResultFound, UserError):
            return {'error': 'Invalid username or password'}, 400
        except Exception as e:
            log.exception(e)
            return {'error': 'Something unexpected went wrong'}, 500

    def delete(self):
        """ Endpoint for loggging out a user """
        # TODO should this be a delete request, or a seperate api endpoint?
        if not current_user.is_authenticated():
            return {'error': 'User is not currently logged in'}, 401
        logout_user(current_user)
        return {'success': 'Logged out successfully'}, 200

api.add_resource(Login, '/api/login')
