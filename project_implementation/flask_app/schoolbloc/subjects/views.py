import logging
from flask import Blueprint
from schoolbloc import auth_required, db
from schoolbloc.subjects.models import Subject
from flask.ext.restful import Api, Resource, abort, reqparse

# Setup logger
log = logging.getLogger(__name__)

# Blueprint and restful settings
mod = Blueprint('subjects', __name__)
api = Api(mod)


def get_subject_or_abort(subject_id):
    # If the user doesn't exist, abort
    subject = Subject.query.get(subject_id)
    if not subject:
        abort(404, message="subject {} doesn't exist".format(subject_id))
    return subject


class subjectApi(Resource):

    @auth_required(roles='admin')
    def get(self, subject_id):
        subject = get_subject_or_abort(subject_id)
        return subject.serialize()

    @auth_required(roles='admin')
    def put(self, subject_id):
        # Optional data
        parser = reqparse.RequestParser()
        parser.add_argument('name')

        # Parse data from incoming request
        args = parser.parse_args()
        name = args.get('name')

        # Update user information and save it to the db. Don't commit the changes
        # until the end, so that if one thing fails this entire request fails
        subject = get_subject_or_abort(subject_id)
        if name:
            subject.name = name
        db.session.add(subject)
        db.session.commit()
        return {'success': 'subject updated successfully'}, 200

    @auth_required(roles='admin')
    def delete(self, subject_id):
        """ Delete an existing User (admins only) """
        subject = get_subject_or_abort(subject_id)
        db.session.delete(subject)
        db.session.commit()
        return {'success': 'subject deleted successfully'}, 200


class subjectListApi(Resource):
    """ Get all users or create new user """

    @auth_required(roles=['admin'])
    def get(self):
        return [subject.serialize() for subject in Subject.query.all()]

    @auth_required(roles='admin')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        args = parser.parse_args()

        s = Subject(name=args['name'])
        db.session.add(s)
        db.session.commit()
        return {'success': 'subject created successfully'}, 200

api.add_resource(subjectApi, '/api/subjects/<int:subject_id>')
api.add_resource(subjectListApi, '/api/subjects')
