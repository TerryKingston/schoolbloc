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


def _get_constraint_foreign_name(orm, constraint):
    """
    Given an orm (model) and constraint (string), return the name of the
    foreign table from the mapping table
    """
    # Get the relationship between the orm object and the mapping table
    mapper_table = orm.__mapper__.relationships.get(constraint)
    relationships = mapper_table.mapper.relationships.items()
    if len(relationships) != 2:
        raise Exception('encountered a constraint mapping table that does not have '
                        'two foreign keys')

    # Figure out which relationship points back to the original orm_object,
    # and which one points to a foreign table
    current_name = orm.__tablename__
    for relationship_name, relationship in relationships:
        if relationship.target.name == current_name:
            continue
        # teacher vs teachers
        foreign_name = relationship_name
        #foreign_name = relationship.target.name
    return foreign_name


class TestRest(Resource):

    def get(self, orm_id):
        orm_object = self._get_or_abort(orm_id)
        ret = orm_object.serialize()
        if not hasattr(self.orm, '__restconstraints__'):
            return ret
        for constraint in orm_object.__restconstraints__:
            foreign_name = _get_constraint_foreign_name(self.orm, constraint)
            foreign_serialized = []
            for mapper_orm in getattr(orm_object, constraint):
                foreign_orm = getattr(mapper_orm, foreign_name)
                serialized = {
                    'id': foreign_orm.id,
                    'value': str(foreign_orm),
                    'active': mapper_orm.active,
                    'priority': mapper_orm.active
                }
                foreign_serialized.append(serialized)
            ret[foreign_name] = foreign_serialized
        return ret

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
        ret = []
        orm_objects = self.orm.query.all()
        for orm_object in orm_objects:
            tmp_ret = orm_object.serialize()
            if not hasattr(self.orm, '__restconstraints__'):
                ret.append(tmp_ret)
                continue
            for constraint in orm_object.__restconstraints__:
                foreign_name = _get_constraint_foreign_name(self.orm, constraint)
                foreign_serialized = []
                for mapper_orm in getattr(orm_object, constraint):
                    foreign_orm = getattr(mapper_orm, foreign_name)
                    serialized = {
                        'id': foreign_orm.id,
                        'value': str(foreign_orm),
                        'active': mapper_orm.active,
                        'priority': mapper_orm.active
                    }
                    foreign_serialized.append(serialized)
                tmp_ret[foreign_name] = foreign_serialized
            ret.append(tmp_ret)
        return ret

    def post(self):
        parser = self._generate_parser()
        request_json = {}  # TODO get json from request

        # Verify received json has required data, and make orm object from said data
        kwargs = {}
        for param in parser['required_params']:
            if param in request_json['payload']:
                kwargs[param] = request_json['payload'][param]
                del request_json['payload'][param]
            else:
                raise Exception('param {} for {} not in payload'.format(param, primary_json['name']))
        for param in parser['optional_params']:
            if param in request_json['optional_params']:
                kwargs[param] = request_json['payload'][param]
                del request_json['payload'][param]
        orm_obj = parser['orm'](**kwargs)
        db.session.add(orm_obj)

        # only stuff left in json_request should be the constraint data. If there
        # is additional keys here, go ahead and error out instead of ignoring them
        for constraint, data in request_json.items():
            if constraint not in parser:
                raise Exception('Unexpected keyword found: {}'.format(constraint))
            try:
                tmp_kwargs = {}
                tmp_kwargs['active'] = request_json[constraint]['active']
                tmp_kwargs['priority'] = request_json[constraint]['priority']
                # TODO get names of orm_key_id and foreigh_key_id
                tmp_kwargs['foreign_key_id'] = request_json[constraint]['active']
                tmp_kwargs['orm_key_id'] = orm_obj.id
                db.session.add(data['orm'](**tmp_kwargs))
            except KeyError as e:
                raise Exception("missing key {} in constraint {}".format(str(e), constraint))

        # Save all new objects to db
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {'error': 'SQL integrity error: {}'.format(e)}, 409
        return {'success': 'Added successfully'}, 200

    def _generate_parser(self):
        """ Adds all the columns of this orm to a parser """
        # Example of what a parser might look like
        parser = {
            'orm': 'Classroom',
            'name': 'classrooms',  # orm.__tablename__
            'required_params': {
                'room_number': str,
            },
            'optional_params': {
                'max_student_count': int,
                'avail_start_time': int,
                'avail_end_time': int,
            },
            'constraints': {  # These should already exist in the db. All optional
                'classrooms_courses': {  # orm.__tablename__
                    'orm': 'ClassroomsCourse',
                    'id': int,  # course.id (id instead of name for uniqueness)
                    'active': bool,
                    'priority': str,
                },
                'teachers': {
                    'orm': 'ClassroomsTeacher',  # mapping table
                    'id': int,  # Teacher id
                    'active': bool,
                    'priority': str,
                },
                'classrooms_timeblock': {
                    'orm': 'ClassroomsTimeblock',
                    'id': int,
                    'active': bool,
                    'priority': str,
                },
            }
        }

        parser = {'required_params': {}, 'optional_params': {}, 'constraints': {}}
        columns = self.orm.__table__.columns.values()
        for column in columns:
            name = column.name
            col_type = column.type
            required = not column.nullable  # nullable == not required

            # Don't let someone specify a primary key
            if name == 'id':
                continue

            # Store type of columnt
            if type(col_type) is db.Integer:
                type = int
            elif type(col_type) is db.Boolean:
                type = bool
            elif type(col_type) is db.String:
                type = str
            else:
                raise Exception("Unknown type {} found".format(col_type))

            # Save data to parser
            if required:
                parser['requred_params'][name] = type
            else:
                parser['optional_params'][name] = type
        return parser

    @staticmethod
    def _generate_constraint(orm_constraint):
        required_keys = ('#TODO_ID', 'active', 'priority')
        columns = orm_constraint.__table__.columns.keys()
        for key in required_keys:
            if key not in columns:
                raise Exception("Expected key {} not found in {}"
                                .format(key, orm_constraint.__tablename__))

        return {
            'orm': orm_constraint,
            'id': int,
            'active': bool,
            'priority': str,
        }

    def _generate_parser(self):
        """
        Dynamically generate a reqparser for every Integer, Boolean, and String
        object in this sqlalchemy table.
        """
        parser = reqparse.RequestParser()
        self._add_orm_to_parser(self.orm, parser)
        if not hasattr(self.orm, '__restconstraints__'):
            return parser
        for orm in self.orm.__restconstraints__:
            parser[orm.__tablename__] = self._generate_constraint(orm)
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
