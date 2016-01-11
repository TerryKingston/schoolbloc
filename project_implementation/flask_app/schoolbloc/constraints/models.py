import logging
from schoolbloc import db

log = logging.getLogger(__name__)


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


class Test1(db.Model, Serializer):
    __tablename__ = 'test1'
    id = db.Column(db.Integer, primary_key=True)
    test_int = db.Column(db.Integer, nullable=False, unique=True)
    test_string = db.Column(db.String)
