import logging
from flask import Blueprint
from schoolbloc import auth_required, db
from schoolbloc.student_groups.models import StudentGroup
from flask.ext.restful import Api, Resource, abort, reqparse

# Setup logger
log = logging.getLogger(__name__)

# Blueprint and restful settings
mod = Blueprint('student_groups', __name__)
api = Api(mod)


def get_student_group_or_abort(student_group_id):
    # If the user doesn't exist, abort
    student_group = StudentGroup.query.get(student_group_id)
    if not student_group:
        abort(404, message="student_group {} doesn't exist".format(student_group_id))
    return student_group


class student_groupApi(Resource):

    @auth_required(roles='admin')
    def get(self, student_group_id):
        student_group = get_student_group_or_abort(student_group_id)
        return student_group.serialize()

    @auth_required(roles='admin')
    def put(self, student_group_id):
        # Optional data
        parser = reqparse.RequestParser()
        parser.add_argument('name')

        # Parse data from incoming request
        args = parser.parse_args()
        name = args.get('name')

        # Update user information and save it to the db. Don't commit the changes
        # until the end, so that if one thing fails this entire request fails
        student_group = get_student_group_or_abort(student_group_id)
        if name:
            student_group.name = name
        db.session.add(student_group)
        db.session.commit()
        return {'success': 'student_group updated successfully'}, 200

    @auth_required(roles='admin')
    def delete(self, student_group_id):
        """ Delete an existing User (admins only) """
        student_group = get_student_group_or_abort(student_group_id)
        db.session.delete(student_group)
        db.session.commit()
        return {'success': 'student_group deleted successfully'}, 200


class student_groupListApi(Resource):
    """ Get all users or create new user """

    @auth_required(roles=['admin'])
    def get(self):
        return [student_group.serialize() for student_group in StudentGroup.query.all()]

    @auth_required(roles='admin')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        args = parser.parse_args()

        s = StudentGroup(name=args['name'])
        db.session.add(s)
        db.session.commit()
        return {'success': 'student_group created successfully'}, 200

api.add_resource(student_groupApi, '/api/student_groups/<int:student_group_id>')
api.add_resource(student_groupListApi, '/api/student_groups')
