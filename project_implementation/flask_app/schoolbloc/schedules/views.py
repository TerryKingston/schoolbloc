import logging

from flask import Blueprint
from flask.ext.restful import Api, Resource, abort
from schoolbloc import auth_required
from schoolbloc.schedules.models import ScheduledClass, ScheduledClassesStudent, \
    Schedule

log = logging.getLogger(__name__)

# Blueprint and restful settings
mod = Blueprint('schedules', __name__)
api = Api(mod)


class ScheduleApi(Resource):
    """ Get/modify/delete a specific user """

    @auth_required(roles='admin')
    def get(self, schedule_id):
        schedule = Schedule.query.filter_by(id=schedule_id).one()
        return [sc.serialize() for sc in schedule.scheduled_classes]

    @auth_required(roles='admin')
    def put(self, schedule_id):
        # TODO
        pass

    @auth_required(roles='admin')
    def delete(self, schedule_id):
        # TODO on delete cascade stuff for schedule_class and schedule_class_students
        pass


class ScheduleListApi(Resource):
    @auth_required(roles='admin')
    def get(self):
        return [schedule.serialize() for schedule in Schedule.query.all()]

    @auth_required(roles='admin')
    def post(self):
        # TODO
        abort(404, message="not yet implemented")


api.add_resource(ScheduleApi, '/api/users/<int:user_id>')
api.add_resource(ScheduleListApi, '/api/users')
