from flask import Blueprint
from flask.ext.restful import Api
from schoolbloc.constraints.restthing import TestRest, TestRestList

from schoolbloc.constraints.models import Test1


def register_rest_orm(orm, endpoint):
    t1 = TestRest
    t1.orm = Test1
    api.add_resource(t1, endpoint + '/<int:orm_id>')

    t1list = TestRestList
    t1list.orm = Test1
    api.add_resource(t1list, endpoint)

mod = Blueprint('api', __name__)
api = Api(mod)

register_rest_orm(Test1, '/api/test1')
