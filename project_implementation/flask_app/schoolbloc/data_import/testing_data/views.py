import logging
from flask import Blueprint
from schoolbloc import auth_required
from schoolbloc.data_import import csv_import
from flask.ext.restful import Api, Resource, abort, reqparse
from werkzeug.datastructures import FileStorage

# Setup logger
log = logging.getLogger(__name__)

# Blueprint and restful settings
mod = Blueprint('data_import', __name__)
api = Api(mod)


class DataImportStudent(Resource):
    """ Get all users or create new user """

    @auth_required(roles='admin')
    def post(self):
        # Check https://gist.github.com/RishabhVerma/7228939
        parser = reqparse.RequestParser()
        parser.add_argument('csv', required=True, type=FileStorage, location='files')
        args = parser.parse_args()
        csv = args['csv']

        # Verify the file extension is .csv
        extension = csv.filename.rsplit('.', 1)[1].lower()
        if '.' in csv.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
            abort(400, message="File extension is not one of our supported types.")

        # TODO figure out how to actually save file and get filepath
        filepath = 'foo'

        try:
            csv_import.students_import(filepath)
            return {'success': 'user created successfully'}, 200
        except Exception as e:
            log.exception(e)
            return {'error': 'something went wrong'}, 409


api.add_resource(DataImportStudent, '/api/import/student')

class DataImportTeacher(Resource):
    """ Get all users or create new user """

    @auth_required(roles='admin')
    def post(self):
        # Check https://gist.github.com/RishabhVerma/7228939
        parser = reqparse.RequestParser()
        parser.add_argument('csv', required=True, type=FileStorage, location='files')
        args = parser.parse_args()
        csv = args['csv']

        # Verify the file extension is .csv
        extension = csv.filename.rsplit('.', 1)[1].lower()
        if '.' in csv.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
            abort(400, message="File extension is not one of our supported types.")

        # TODO figure out how to actually save file and get filepath
        filepath = 'foo'

        try:
            csv_import.teachers_import(filepath)
            return {'success': 'user created successfully'}, 200
        except Exception as e:
            log.exception(e)
            return {'error': 'something went wrong'}, 409


api.add_resource(DataImportTeacher, '/api/import/teacher')


class DataImportCourse(Resource):
    """ Get all users or create new user """

    @auth_required(roles='admin')
    def post(self):
        # Check https://gist.github.com/RishabhVerma/7228939
        parser = reqparse.RequestParser()
        parser.add_argument('csv', required=True, type=FileStorage, location='files')
        args = parser.parse_args()
        csv = args['csv']

        # Verify the file extension is .csv
        extension = csv.filename.rsplit('.', 1)[1].lower()
        if '.' in csv.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
            abort(400, message="File extension is not one of our supported types.")

        # TODO figure out how to actually save file and get filepath
        filepath = 'foo'

        try:
            csv_import.courses_import(filepath)
            return {'success': 'user created successfully'}, 200
        except Exception as e:
            log.exception(e)
            return {'error': 'something went wrong'}, 409


api.add_resource(DataImportCourse, '/api/import/course')

class DataImportClassroom(Resource):
    """ Get all users or create new user """

    @auth_required(roles='admin')
    def post(self):
        # Check https://gist.github.com/RishabhVerma/7228939
        parser = reqparse.RequestParser()
        parser.add_argument('csv', required=True, type=FileStorage, location='files')
        args = parser.parse_args()
        csv = args['csv']

        # Verify the file extension is .csv
        extension = csv.filename.rsplit('.', 1)[1].lower()
        if '.' in csv.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
            abort(400, message="File extension is not one of our supported types.")

        # TODO figure out how to actually save file and get filepath
        filepath = 'foo'

        try:
            csv_import.classrooms_import(filepath)
            return {'success': 'user created successfully'}, 200
        except Exception as e:
            log.exception(e)
            return {'error': 'something went wrong'}, 409


api.add_resource(DataImportClassroom, '/api/import/classroom')
