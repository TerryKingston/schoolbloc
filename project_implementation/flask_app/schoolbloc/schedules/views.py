import logging

from flask import Blueprint
from flask.ext.restful import Api, Resource, abort, reqparse
from schoolbloc import auth_required
from schoolbloc.scheduler.scheduler import Scheduler
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
    # @auth_required(roles='admin')
    def get(self):
        return [schedule.serialize() for schedule in Schedule.query.all()]

    @auth_required(roles='admin')
    def post(self):
        # TODO somehow pass the name in and have it saved as that in the db
        #parser = reqparse.RequestParser()
        #parser.add_argument('name', required=True)
        #args = parser.parse_args()
        scheduler = Scheduler()
        scheduler.make_schedule()

        # TODO this only allows for one schedule right now
        schedule = Schedule.query.first()
        return [sc.serialize() for sc in schedule.scheduled_classes]

api.add_resource(ScheduleApi, '/api/schedules/<int:schedule_id>')
api.add_resource(ScheduleListApi, '/api/schedules')
