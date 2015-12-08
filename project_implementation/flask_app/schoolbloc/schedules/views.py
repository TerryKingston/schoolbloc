import logging

from flask import Blueprint
from flask.ext.restful import Api, Resource

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
        """
        [
          {
            "teacher": {"id": 1, "first_name": "Severus", "last_name": "snape"},
            "classroom": {"id": 1, "room_number": 101, "max_student_count": 15},
            "start_time": 0800,
            "end_time": 1000,
            "course": {"id": 1, "name": "Remedial Potions", "duration": 120, "max_student_count": 30, "min_student_count": 10}
            "students": [
                          {"id": 1, "first_name": "Harry", "last_name": "Potter"},
                          {"id": 2, "first_name": "Ron", "last_name": "Weasly"}
                        ]
          }
        ]
        """
        schedule = Schedule.query.filter_by(id=schedule_id).one()
        return [sc.serialize() for sc in schedule.scheduled_classes]
