from flask import Blueprint
from flask.ext.restful import Api
from schoolbloc.constraints.restthing import TestRest, TestRestList

from schoolbloc.constraints.models import Test1, Test2


mod = Blueprint('api', __name__)
api = Api(mod)


class Serializer:
    """
    Provides a base model for our database tables and constraints. This
    provides a serialize method that will be utilized by our rest endpoints
    """
    def serialize(self):
        results = {}
        columns = self.__table__.columns.values()
        for column in columns:
            results[column.name] = getattr(self, column.name)
        return results


def register_rest_orm(orm):
    name = orm.__tablename__
    cls = type(name, (TestRest, Serializer), {'orm': orm})
    api.add_resource(cls, '/api/{}/<int:orm_id>'.format(name))

    cls_list = type(name + 'list', (TestRestList, Serializer), {'orm': orm})
    api.add_resource(cls_list, '/api/{}'.format(name))

register_rest_orm(Test1)
register_rest_orm(Test2)
