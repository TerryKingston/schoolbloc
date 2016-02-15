import logging
from flask.ext.restful import Resource, reqparse, abort
from jinja2 import Template
from schoolbloc import db
from sqlalchemy.exc import IntegrityError

log = logging.getLogger(__name__)

rest_template = Template(
"""
Manage {{ orm }} (/api/{{ orm }}/<int:{{ orm }}_id>)
=========================================================
The endpoint for viewing/modifying/deleting individual {{ orm }}.
If you pass in a {{ orm }}_id that doesn't exist in the database, a
404 is returned with the message "{{ orm }} ID <id> not found"

GET request - returns a json dict representation of this {{ orm }} containing the following keys:
{% for id in ids %}
              - {{ id[0] }} ({{ id[1] }})
{%- endfor %}

DELETE request - removes the given {{ orm }}. Returns {'success': True} (code 200) on success and
                 {'error': <err_msg>} (code 409) on failure

PUT request - updates the data for this course. it will return {'success': True}
              (code 200) on success, {'error': <err_msg>} (code 409) on failure.
              It takes any number of the following optional args:
{% for arg in args %}
                - {{ arg[0] }} ({{ arg[1] }})
{%- endfor %}
"""
)

list_rest_template = Template(
"""
List/Create {{ orm }} (/api/{{ orm }})
===============================
The endpoint for listing all {{ orm }} and creating new {{ orm }}.

GET request - return a json list of all {{ orm }}s

POST request - create a new {{ orm }}. This will return '{success': 'Added successfully'}
               (code 200) on success, or {'error': <err_msg>} (code 409) on failure.
               It takes the following args:
{% for arg in args %}
                - {{ arg[0] }} ({{ arg[1] }})   # {{ arg[2] }}
{%- endfor %}

"""
)


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

    def generate_docs(self):
        ids = []
        args = []
        orm_name = self.orm.__tablename__
        columns = self.orm.__table__.columns.values()
        for column in columns:
            name = column.name
            type = str(column.type)
            required = not column.nullable
            ids.append((name, type))
            if name != 'id':
                args.append((name, type, required))
        return rest_template.render(orm=orm_name, ids=ids, args=args)


class TestRestList(Resource):

    def get(self):
        return [orm_obj.serialize() for orm_obj in self.orm.query.all()]

    def post(self):
        parser = self._generate_parser()
        request_json = {}  # TODO get json from request

        # Get the json of the primary object of this api call (ie, if this was a
        # call to /api/classrooms, the primary object would be a Classroom object)
        primary_json = None
        for key, value in parser.items():
            if value['primary']:
                primary_json = value

        # Verify received json has correct data, and make orm object
        kwargs = {}
        for param in primary_json['required_params']:
            if param in request_json['payload']:
                kwargs[param] = request_json['payload'][param]
                del request_json['payload'][param]
            else:
                raise Exception('param {} for {} not in payload'.format(param, primary_json['name']))
        for param in request_json['payload']:
            if param in primary_json['optional_params']:
                kwargs[param] = request_json['payload'][param]
                del request_json['payload'][param]
        primary_orm_obj = primary_json['orm'](**kwargs)

        # Verify constraint data and create constraints



        # Save to db
        try:
            orm_object = self.orm(**kwargs)
            db.session.add(orm_object)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error': 'SQL integrity error'}, 409
        return {'success': 'Added successfully'}, 200

    @staticmethod
    def _add_orm_to_parser(orm, parser):
        """ Adds all the columns of this orm to a parser """
        # Example of what a parser might look like
        parser = {
            'orm': Classroom,
            'name': 'classrooms',  # orm.__tablename__
            'required_params': {
                'room_number': str,
            },
            'optional_params': {
                'max_student_count': int,
                'avail_start_time': int,
                'avail_end_time': int,
            },
            'constraints': {  # These should already exist in the db
                'classrooms_courses': {  # orm.__tablename__
                    'orm': ClassroomsCourse,
                    'id': int,  # course.id (id instead of name for uniqueness)
                    'active': bool,
                    'priority': str,
                },
                'classrooms_teachers': {
                    'orm': ClassroomsTeacher,
                    'id': int,
                    'active': bool,
                    'priority': str,
                },
                'classrooms_courses': {
                    'orm': ClassroomsCourse,
                    'id': int,
                    'active': bool,
                    'priority': str,
                },
            }
        }

        columns = orm.__table__.columns.values()
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

    def _generate_parser(self):
        """
        Dynamically generate a reqparser for every Integer, Boolean, and String
        object in this sqlalchemy table.
        """
        parser = reqparse.RequestParser()
        self._add_orm_to_parser(self.orm, parser)
        if not hasattr(self.orm, '__restfulbinds__'):
            return parser
        for orm in self.orm.__restfulbinds__:
            self._add_orm_to_parser(orm, parser)
        return parser

    def generate_docs(self):
        ids = []
        args = []
        orm_name = self.orm.__tablename__
        columns = self.orm.__table__.columns.values()
        for column in columns:
            name = column.name
            type = str(column.type)
            if not column.nullable:
                required = 'Required'
            else:
                required = 'Optional'
            ids.append((name, type))
            if name != 'id':
                args.append((name, type, required))
        return list_rest_template.render(orm=orm_name, ids=ids, args=args)
