import logging
from flask import Blueprint
from flask.ext.jwt import current_identity
from schoolbloc import auth_required, db
from schoolbloc.teachers.models import Teacher
from flask.ext.restful import Api, Resource, abort, reqparse

# Setup logger
log = logging.getLogger(__name__)

# Blueprint and restful settings
mod = Blueprint('teacher', __name__)
api = Api(mod)
