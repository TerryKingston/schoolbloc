import logging

from flask import request
from flask.ext.restful import Resource, reqparse, abort
from jinja2 import Template
from sqlalchemy.orm.exc import NoResultFound

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


# TODO instead of raising exceptions, call abort with an appropiate json message
#      and http status code


def _find_constraint_mapping_table(orm, constraint_str):
    """
    If called on the orm object Classroom with the constraint_str 'teacher',
    this should return ClassroomsTeachers (as it is the constraint mapping
    table that ties Classroom and Teacher together. It searches
    __restconstraints__ for this data.

    The string needs to match what the actual relationship is called for
    this to work. In this example, 'teacher' would work but 'teachers'
    would fail because the relationship is defined as:
    teacher = db.relationship("Teacher", backref="classrooms_teachers")
    """
    if not hasattr(orm, '__restconstraints__'):
        raise Exception('no __restconstraints__ defined on {}'.format(orm))
    for table_constraint in orm.__restconstraints__:
        mapper_table = orm.__mapper__.relationships.get(table_constraint)
        relationships = mapper_table.mapper.relationships.keys()
        if len(relationships) != 2:
            raise Exception('encountered a constraint mapping table that does not have '
                            'two foreign keys')
        if constraint_str in relationships:
            # this is the table we are looking for. Return the actual ORM
            # object, not the table name or relationship property objects
            return mapper_table.mapper.class_
    raise Exception('No table found under __restconstraints__ which maps'
                    '{} to {}'.format(orm.__tablename__, constraint_str))


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


def _get_constraint_key_column_names(base_orm, foreign_orm):
    # Get the column names for the foreign key ids in this constraint
    for column in foreign_orm.__mapper__.columns.values():
        for foreign_key in column.foreign_keys:
            if foreign_key.column.table.name == base_orm.__tablename__:
                this_id_name = column.name
            else:
                foreign_id_name = column.name
    if not this_id_name or not foreign_id_name:  # Sanity check
        raise Exception('Failed to pull out id column name')
    return this_id_name, foreign_id_name


def _generate_parser(orm):
    """
    Adds all the columns of this orm to a parser

    Here is what a parser might look like:

    parser = {
        'required_params': {
            'room_number': str,
        },
        'optional_params': {
            'max_student_count': int,
            'avail_start_time': int,
            'avail_end_time': int,
        },
    }
    """
    parser = {'required_params': {}, 'optional_params': {}}
    columns = orm.__table__.columns.values()
    for column in columns:
        name = column.name
        col_type = column.type
        required = not column.nullable  # nullable == not required

        # TODO actually check form primary key, instead of assuming its called id
        # Don't let someone specify a primary key
        if name == 'id':
            continue

        # Store type of column
        if type(col_type) is db.Integer:
            col_type = int
        elif type(col_type) is db.Boolean:
            col_type = bool
        elif type(col_type) is db.String:
            col_type = str
        else:
            raise Exception("Unknown type {} found".format(col_type))

        # Save data to parser
        if required:
            parser['required_params'][name] = col_type
        else:
            parser['optional_params'][name] = col_type
    return parser


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
        orm_obj = self._get_or_abort(orm_id)
        parser = _generate_parser(self.orm)
        request_json = request.get_json(force=True)
        if 'payload' not in request_json:
            raise Exception('missing key: "payload" from json request')

        # TODO verify json datatype to what parser says it should be
        # As this is editing existing data, we will treat everything as optional
        to_remove = []  # Cannot remove elements from dict while iterating
        for key, value in request_json['payload'].items():
            if key in parser['required_params'] or key in parser['optional_params']:
                setattr(orm_obj, key, value)  # Update orm object with n
                to_remove.append(key)
        for key in to_remove:
            del request_json['payload'][key]
        db.session.add(orm_obj)

        # only stuff left in json_request should be the constraint data. If there
        # is additional keys here, go ahead and error out instead of ignoring them
        # (nothing has been commited to the db yet)
        for constraint, requests in request_json['payload'].items():
            for data in requests:
                if 'method' not in data:
                    raise Exception('Must have method (add/edit/delete) in constraint payload')
                if data['method'] not in ('add', 'edit', 'delete'):
                    raise Exception('method in constraint payload must be add, edit, or delete')

                orm_class = _find_constraint_mapping_table(self.orm, constraint)
                this_id, foreign_id = _get_constraint_key_column_names(self.orm, orm_class)

                if data['method'] == 'add':
                    try:
                        tmp_kwargs = {}
                        tmp_kwargs['active'] = data['active']
                        tmp_kwargs['priority'] = data['priority']
                        tmp_kwargs[this_id] = orm_obj.id
                        tmp_kwargs[foreign_id] = data['id']
                        db.session.add(orm_class(**tmp_kwargs))
                    except KeyError as e:
                        raise Exception("missing key {} in constraint {}".format(str(e), constraint))

                elif data['method'] == 'delete':
                    try:
                        # filter operates on columns, not strings
                        this_col = getattr(orm_class, this_id)
                        foreign_col = getattr(orm_class, foreign_id)
                        tmp_orm_obj = orm_class.query.filter(this_col == orm_obj.id,
                                                             foreign_col == data['id']).one()
                        db.session.delete(tmp_orm_obj)
                    except NoResultFound:
                        raise Exception("Cannot find constraint of type {} with {}={} "
                                        "and {}={}".format(orm_class.__tablename__,
                                                           this_id, orm_obj.id,
                                                           foreign_id, data['id']))

                elif data['method'] == 'edit':
                    try:
                        # filter operates on columns, not strings
                        this_col = getattr(orm_class, this_id)
                        foreign_col = getattr(orm_class, foreign_id)
                        tmp_orm_obj = orm_class.query.filter(this_col == orm_obj.id,
                                                             foreign_col == data['id']).one()

                        for key, value in data.items():
                            if key == 'id':
                                setattr(tmp_orm_obj, foreign_id, value)
                            elif key == 'active':
                                setattr(tmp_orm_obj, 'active', value)
                            elif key == 'priority':
                                setattr(tmp_orm_obj, 'priority', value)
                            elif key == 'method':
                                continue
                            else:
                                raise Exception('Bad key found in constraint json: {}'.format(key))
                        db.session.add(tmp_orm_obj)
                    except NoResultFound:
                        raise Exception("Cannot find constraint of type {} with {}={} "
                                        "and {}={}".format(orm_class.__tablename__,
                                                           this_id, orm_obj.id,
                                                           foreign_id, data['id']))

        # Save all changes made into the db, rollback and error if that fails
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {'error': 'SQL integrity error: {}'.format(e)}, 409
        return {'success': 'Updated successfully'}, 200

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
        parser = _generate_parser(self.orm)
        request_json = request.get_json(force=True)
        if 'payload' not in request_json:
            raise Exception('missing key: "payload" from json request')

        # TODO verify json datatype to what parser says it should be
        # Verify received json has required data, and make orm object from said data
        kwargs = {}
        for param in parser['required_params']:
            if param in request_json['payload']:
                kwargs[param] = request_json['payload'][param]
                del request_json['payload'][param]
            else:
                raise Exception('Required param {} for {} not in payload'.format(param, parser['name']))
        for param in parser['optional_params']:
            if param in request_json['payload']:
                kwargs[param] = request_json['payload'][param]
                del request_json['payload'][param]
        orm_obj = self.orm(**kwargs)
        db.session.add(orm_obj)
        db.session.flush()

        # only stuff left in json_request should be the constraint data. If there
        # is additional keys here, go ahead and error out instead of ignoring them
        # (nothing has been commited to the db yet)
        for constraint, data in request_json['payload'].items():
            try:
                orm_class = _find_constraint_mapping_table(self.orm, constraint)
                this_id, foreign_id = _get_constraint_key_column_names(self.orm, orm_class)

                tmp_kwargs = {}
                tmp_kwargs['active'] = data['active']
                tmp_kwargs['priority'] = data['priority']
                tmp_kwargs[this_id] = orm_obj.id
                tmp_kwargs[foreign_id] = data['id']
                db.session.add(orm_class(**tmp_kwargs))
            except KeyError as e:
                raise Exception("missing key {} in constraint {}".format(str(e), constraint))

        # Save all new objects to db
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {'error': 'SQL integrity error: {}'.format(e)}, 409
        return {'success': 'Added successfully'}, 200


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
