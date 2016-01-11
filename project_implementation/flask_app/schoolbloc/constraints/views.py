from flask import Blueprint
from flask.ext.restful import Api
from schoolbloc.constraints.restthing import TestRest, TestRestList

from schoolbloc.constraints.models import Test1, Test2


mod = Blueprint('api', __name__)
api = Api(mod)


def register_rest_orm(orm):
    name = orm.__tablename__
    cls = type(name, (TestRest,), {'orm': orm})
    api.add_resource(cls, '/api/{}/<int:orm_id>'.format(name))

    cls_list = type(name + 'list', (TestRestList,), {'orm': orm})
    api.add_resource(cls_list, '/api/{}'.format(name))

register_rest_orm(Test1)
register_rest_orm(Test2)
