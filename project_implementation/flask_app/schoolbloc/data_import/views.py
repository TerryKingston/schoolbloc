import logging
import os
from flask import Blueprint, request, Flask
from schoolbloc import auth_required
from schoolbloc.data_import import csv_import
from flask.ext.restful import Api, Resource, abort
from werkzeug import secure_filename

# Setup logger
log = logging.getLogger(__name__)

# Blueprint and restful settings
mod = Blueprint('data_import', __name__)
api = Api(mod)

app = Flask(__name__)
# TODO: these should be moved to the config file
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])
app.config['TMP_FOLDER'] = '///../tmp/' # maybe pick a better place for temp files?


class DataImportStudent(Resource):
    """ Get all users or create new user """

    #@auth_required(roles='admin')
    def post(self):
        csv = request.files['file']

        if not csv:
            abort(400, message="Missing import file")

        # Verify the file extension is .csv
        extension = csv.filename.rsplit('.', 1)[1].lower()
        if '.' in csv.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
            abort(400, message="File extension is not one of our supported types.")

        filename = secure_filename(csv.filename) # scrub file path 
        tmp_filepath = os.path.join(app.config['TMP_FOLDER'], filename)
        csv.save(tmp_filepath)

        try:
            csv_import.students_import(tmp_filepath)
            return {'success': 'Student data imported successfully'}, 200
        except Exception as e:
            log.exception(e)
            return {'error': 'something went wrong'}, 409


class DataImportTeacher(Resource):
    """ Get all users or create new user """

    #@auth_required(roles='admin')
    def post(self):
        csv = request.files['file']

        if not csv:
            abort(400, message="Missing import file")

        # Verify the file extension is .csv
        extension = csv.filename.rsplit('.', 1)[1].lower()
        if '.' in csv.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
            abort(400, message="File extension is not one of our supported types.")

        filename = secure_filename(csv.filename) # scrub file path 
        tmp_filepath = os.path.join(app.config['TMP_FOLDER'], filename)
        csv.save(tmp_filepath)

        try:
            csv_import.teachers_import(tmp_filepath)
            return {'success': 'Teacher data imported successfully'}, 200
        except Exception as e:
            log.exception(e)
            return {'error': 'something went wrong'}, 409


class DataImportCourse(Resource):
    """ Get all users or create new user """

    #@auth_required(roles='admin')
    def post(self):
        csv = request.files['file']

        if not csv:
            abort(400, message="Missing import file")

        # Verify the file extension is .csv
        extension = csv.filename.rsplit('.', 1)[1].lower()
        if '.' in csv.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
            abort(400, message="File extension is not one of our supported types.")

        filename = secure_filename(csv.filename) # scrub file path 
        tmp_filepath = os.path.join(app.config['TMP_FOLDER'], filename)
        csv.save(tmp_filepath)

        try:
            csv_import.courses_import(tmp_filepath)
            return {'success': 'Course data imported successfully'}, 200
        except Exception as e:
            log.exception(e)
            return {'error': 'something went wrong'}, 409


class DataImportClassroom(Resource):
    """ Get all users or create new user """

    #@auth_required(roles='admin')
    def post(self):
        csv = request.files['file']

        if not csv:
            abort(400, message="Missing import file")

        # Verify the file extension is .csv
        extension = csv.filename.rsplit('.', 1)[1].lower()
        if '.' in csv.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
            abort(400, message="File extension is not one of our supported types.")

        filename = secure_filename(csv.filename) # scrub file path 
        tmp_filepath = os.path.join(app.config['TMP_FOLDER'], filename)
        csv.save(tmp_filepath)

        try:
            csv_import.classrooms_import(tmp_filepath)
            return {'success': 'Classroom data imported successfully'}, 200
        except Exception as e:
            log.exception(e)
            return {'error': 'something went wrong'}, 409

class DataImportStudentGroup(Resource):
    """ Get all users or create new user """

    #@auth_required(roles='admin')
    def post(self):
        csv = request.files['file']

        if not csv:
            abort(400, message="Missing import file")

        # Verify the file extension is .csv
        extension = csv.filename.rsplit('.', 1)[1].lower()
        if '.' in csv.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
            abort(400, message="File extension is not one of our supported types.")

        filename = secure_filename(csv.filename) # scrub file path
        tmp_filepath = os.path.join(app.config['TMP_FOLDER'], filename)
        csv.save(tmp_filepath)

        try:
            csv_import.student_groups_import(tmp_filepath)
            return {'success': 'Classroom data imported successfully'}, 200
        except Exception as e:
            log.exception(e)
            return {'error': 'something went wrong'}, 409

class DataImportSubject(Resource):
    """ Get all users or create new user """

    #@auth_required(roles='admin')
    def post(self):
        csv = request.files['file']

        if not csv:
            abort(400, message="Missing import file")

        # Verify the file extension is .csv
        extension = csv.filename.rsplit('.', 1)[1].lower()
        if '.' in csv.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
            abort(400, message="File extension is not one of our supported types.")

        filename = secure_filename(csv.filename) # scrub file path
        tmp_filepath = os.path.join(app.config['TMP_FOLDER'], filename)
        csv.save(tmp_filepath)

        try:
            csv_import.subjects_import(tmp_filepath)
            return {'success': 'Classroom data imported successfully'}, 200
        except Exception as e:
            log.exception(e)
            return {'error': 'something went wrong'}, 409

class DataImportTimeblock(Resource):
    """ Get all users or create new user """

    #@auth_required(roles='admin')
    def post(self):
        csv = request.files['file']

        if not csv:
            abort(400, message="Missing import file")

        # Verify the file extension is .csv
        extension = csv.filename.rsplit('.', 1)[1].lower()
        if '.' in csv.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
            abort(400, message="File extension is not one of our supported types.")

        filename = secure_filename(csv.filename) # scrub file path
        tmp_filepath = os.path.join(app.config['TMP_FOLDER'], filename)
        csv.save(tmp_filepath)

        try:
            csv_import.timeblocks_import(tmp_filepath)
            return {'success': 'Classroom data imported successfully'}, 200
        except Exception as e:
            log.exception(e)
            return {'error': 'something went wrong'}, 409


api.add_resource(DataImportStudent, '/api/import/student')
api.add_resource(DataImportTeacher, '/api/import/teacher')
api.add_resource(DataImportCourse, '/api/import/course')
api.add_resource(DataImportClassroom, '/api/import/classroom')
api.add_resource(DataImportStudentGroup, '/api/import/student_group')
api.add_resource(DataImportSubject, '/api/import/subject')
api.add_resource(DataImportTimeblock, '/api/import/timeblock')
