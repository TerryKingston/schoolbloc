import logging
from flask.ext.restful import Resource, reqparse, abort
from schoolbloc import db
from sqlalchemy.exc import IntegrityError

log = logging.getLogger(__name__)


class TestRest(Resource):

    def get(self, orm_id):
        orm_object = self._get_or_abort(orm_id)
        return orm_object.serialize()

    def put(self, orm_id):
        # Argument parser
        parser = self._generate_parser()
        args = parser.parse_args()

        # Get current orm object or abort
        orm_object = self._get_or_abort(orm_id)

        # Update anything that was requested
        columns = self.orm.__table__.columns.values()
        for column in columns:
            name = column.name
            if name in args:
                setattr(orm_object, name, args[name])
        db.session.add(orm_object)
        db.session.commit()
        return {'success': True}

    def delete(self, orm_id):
        orm_object = self._get_or_abort(orm_id)
        db.session.delete(orm_object)
        db.session.commit()
        return {'success': True}

    def _get_or_abort(self, orm_id):
        orm_object = self.orm.query.get(orm_id)
        if not orm_object:
            abort(404, message="ID {} not found".format(orm_id))
        return orm_object

    def _generate_parser(self):
        """
        Dynamically generate a reqparser for every Integer, Boolean, and String
        object in this sqlalchemy table.
        """
        parser = reqparse.RequestParser()

        columns = self.orm.__table__.columns.values()
        for column in columns:
            name = column.name
            col_type = column.type

            # Don't let someone change the primary id through the rest api
            if name == 'id':
                continue

            if type(col_type) is db.Integer:
                parser.add_argument(name, type=int, store_missing=False)
            elif type(col_type) is db.Boolean:
                parser.add_argument(name, store_missing=False)
            elif type(col_type) is db.String:
                parser.add_argument(name, store_missing=False)
            else:
                raise Exception("Unknown type {} found".format(col_type))

        return parser


class TestRestList(Resource):

    def get(self):
        return [orm_obj.serialize() for orm_obj in self.orm.query.all()]

    def post(self):
        parser = self._generate_parser()
        kwargs = parser.parse_args()
        try:
            orm_object = self.orm(**kwargs)
            db.session.add(orm_object)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error': 'SQL integrity error'}, 409
        return {'success': 'Added successfully'}, 200

    def _generate_parser(self):
        """
        Dynamically generate a reqparser for every Integer, Boolean, and String
        object in this sqlalchemy table.
        """
        parser = reqparse.RequestParser()

        columns = self.orm.__table__.columns.values()
        for column in columns:
            name = column.name
            col_type = column.type
            required = not column.nullable  # nullable == not required

            # Don't let someone specify a primary key
            if name == 'id':
                continue

            if type(col_type) is db.Integer:
                parser.add_argument(name, type=int, required=required, store_missing=False)
            elif type(col_type) is db.Boolean:
                parser.add_argument(name, type=bool, required=required, store_missing=False)
            elif type(col_type) is db.String:
                parser.add_argument(name, required=required, store_missing=False)
            else:
                raise Exception("Unknown type {} found".format(col_type))

        return parser
