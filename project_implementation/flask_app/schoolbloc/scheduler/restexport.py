import logging
from flask import request
from flask.ext.restful import Resource, abort
from sqlalchemy.orm.exc import NoResultFound
from schoolbloc import db
from sqlalchemy.exc import IntegrityError


log = logging.getLogger(__name__)


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
        abort(400, message='Received constraint {}, however no constraints are defined '
                           'in __restconstraints__. Is the model correct?'.format(constraint_str))
    for table_constraint in orm.__restconstraints__:
        mapper_table = orm.__mapper__.relationships.get(table_constraint)
        relationships = mapper_table.mapper.relationships.keys()
        if len(relationships) != 2:
            abort(400, message='encountered a constraint mapping table that does not have '
                               'two foreign keys')
        if constraint_str in relationships:
            # this is the table we are looking for. Return the actual ORM
            # object, not the table name or relationship property objects
            return mapper_table.mapper.class_
    abort(400, message='No table found under __restconstraints__ which maps'
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
        abort(400, message='encountered a constraint mapping table that does not have '
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
        abort(400, message='Failed to pull out id column name')
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
            abort(400, message="Unknown type {} found".format(col_type))

        # Save data to parser
        if required:
            parser['required_params'][name] = col_type
        else:
            parser['optional_params'][name] = col_type
    return parser


class TestRest(Resource):

    def get(self, orm_id):
        get_constraints = request.args.get('constraints')
        orm_object = self._get_or_abort(orm_id)
        ret = orm_object.serialize()
        if not hasattr(self.orm, '__restconstraints__'):
            return ret
        if get_constraints and get_constraints.lower() == 'false':
            return ret
        for constraint in orm_object.__restconstraints__:
            foreign_name = _get_constraint_foreign_name(self.orm, constraint)
            foreign_serialized = []
            for mapper_orm in getattr(orm_object, constraint):
                # Data from foreign orm
                foreign_orm = getattr(mapper_orm, foreign_name)
                serialized = {
                    'id': foreign_orm.id,
                    'value': str(foreign_orm),
                }

                # Constraint orm data
                for column in mapper_orm.__table__.columns.values():
                    if not column.foreign_keys and not column.primary_key:
                        serialized[column.name] = getattr(mapper_orm, column.name)
                foreign_serialized.append(serialized)
            ret[foreign_name] = foreign_serialized
        return ret

    def put(self, orm_id):
        orm_obj = self._get_or_abort(orm_id)
        parser = _generate_parser(self.orm)
        request_json = request.get_json(force=True)

        # TODO verify json datatype to what parser says it should be
        # As this is editing existing data, we will treat everything as optional
        to_remove = []  # Cannot remove elements from dict while iterating
        for key, value in request_json.items():
            if key in parser['required_params'] or key in parser['optional_params']:
                setattr(orm_obj, key, value)  # Update orm object with n
                to_remove.append(key)
        for key in to_remove:
            del request_json[key]
        db.session.add(orm_obj)

        # only stuff left in json_request should be the constraint data. If there
        # is additional keys here, go ahead and error out instead of ignoring them
        # (nothing has been commited to the db yet)
        for constraint, requests in request_json.items():
            for data in requests:
                if 'method' not in data:
                    abort(400, message='Must have method (add/edit/delete) in constraint payload')
                if data['method'] not in ('add', 'edit', 'delete'):
                    abort(400, message='method in constraint payload must be add, edit, or delete')

                orm_class = _find_constraint_mapping_table(self.orm, constraint)
                this_id, foreign_id = _get_constraint_key_column_names(self.orm, orm_class)

                if data['method'] == 'add':
                    # These are the ids for the constraint
                    tmp_kwargs = {
                        this_id: orm_obj.id,
                        foreign_id: data['id']
                    }

                    # These are the additional data for the constraints (active,
                    # priority, etc). Don't error out here if the key doesn't
                    # exist in the request json. If it is a nullable column, or
                    # if the column has a default value, they don't have to pass
                    # it in here for the api to work
                    for column in orm_class.__table__.columns.values():
                        if not column.foreign_keys and not column.primary_key:
                            try:
                                tmp_kwargs[column.name] = data[column.name]
                            except KeyError:
                                pass
                    db.session.add(orm_class(**tmp_kwargs))

                elif data['method'] == 'delete':
                    try:
                        # filter operates on columns, not strings
                        this_col = getattr(orm_class, this_id)
                        foreign_col = getattr(orm_class, foreign_id)
                        tmp_orm_obj = orm_class.query.filter(this_col == orm_obj.id,
                                                             foreign_col == data['id']).one()
                        db.session.delete(tmp_orm_obj)
                    except NoResultFound:
                        abort(400, message="Cannot find constraint of type {} with {}={} "
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
                            # Special keys we want to handle or ignore
                            if key == 'id':
                                setattr(tmp_orm_obj, foreign_id, value)
                                continue
                            elif key == 'method':
                                continue

                            # Columns of the constraint orm
                            found = False
                            for column in orm_class.__table__.columns.values():
                                if key == column.name:
                                    setattr(tmp_orm_obj, key, value)
                                    found = True
                                    break
                            if not found:
                                abort(400, message='Bad key found in constraint json: {}'.format(key))
                        db.session.add(tmp_orm_obj)
                    except NoResultFound:
                        abort(400, message="Cannot find constraint of type {} with {}={} "
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


class TestRestList(Resource):

    def get(self):
        get_constraints = request.args.get('constraints')
        ret = []
        orm_objects = self.orm.query.all()
        for orm_object in orm_objects:
            tmp_ret = orm_object.serialize()
            if not hasattr(self.orm, '__restconstraints__'):
                ret.append(tmp_ret)
                continue
            if get_constraints and get_constraints.lower() == 'false':
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
                    }
                    for column in mapper_orm.__table__.columns.values():
                        if not column.foreign_keys and not column.primary_key:
                            serialized[column.name] = getattr(mapper_orm, column.name)
                    foreign_serialized.append(serialized)
                tmp_ret[foreign_name] = foreign_serialized
            ret.append(tmp_ret)
        return ret

    def post(self):
        parser = _generate_parser(self.orm)
        request_json = request.get_json(force=True)

        # TODO verify json datatype to what parser says it should be
        # Verify received json has required data, and make orm object from said data
        kwargs = {}
        for param in parser['required_params']:
            if param in request_json:
                kwargs[param] = request_json[param]
                del request_json[param]
            else:
                abort(400, message='Required param {} not in payload'.format(param))
        for param in parser['optional_params']:
            if param in request_json:
                kwargs[param] = request_json[param]
                del request_json[param]
        orm_obj = self.orm(**kwargs)
        db.session.add(orm_obj)
        db.session.flush()

        # only stuff left in json_request should be the constraint data. If there
        # is additional keys here, go ahead and error out instead of ignoring them
        # (nothing has been commited to the db yet)
        for constraint, data_list in request_json.items():
            for data in data_list:
                constraint_orm_class = _find_constraint_mapping_table(self.orm, constraint)
                this_id, foreign_id = _get_constraint_key_column_names(self.orm, constraint_orm_class)

                # These are the ids for the constraint
                tmp_kwargs = {
                    this_id: orm_obj.id,
                    foreign_id: data['id']
                }

                # These are the additional data for the constraints (active,
                # priority, etc). Don't error out here if the key doesn't
                # exist in the request json. If it is a nullable column, or
                # if the column has a default value, they don't have to pass
                # it in here for the api to work
                for column in constraint_orm_class.__table__.columns.values():
                    if not column.foreign_keys and not column.primary_key:
                        try:
                            tmp_kwargs[column.name] = data[column.name]
                        except KeyError:
                            pass
                db.session.add(constraint_orm_class(**tmp_kwargs))

        # Save all new objects to db
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'error': 'Error committing SQL: {}'.format(e)}, 409
        return {'success': 'Added successfully'}, 200
