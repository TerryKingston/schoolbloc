import logging
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CsrfProtect

# Create a logger to be used
log = logging.getLogger(__name__)

# Create the flask application
app = Flask(__name__)
app.config.from_object('config')

# Create the sqlalchemy database object. The actual database configuration is
# defined in config.py so we can swap between dev and production with only
# having to change that one file
db = SQLAlchemy(app)

# Enable csrf protection on all POST requests
csrf = CsrfProtect(app)


@app.before_request
def regenerate_session():
    """
    Use this to keep a user logged in if they keep using the application. This
    is optional, we could keep a user logged in until they close their browser
    if we wanted, or we could use this to have a user logged out after so long
    of inactivity
    """
    pass  # TODO


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
app.register_blueprint(blueprint_module)
