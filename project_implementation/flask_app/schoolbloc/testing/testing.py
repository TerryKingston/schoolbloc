import unittest
from flask import json
from sqlalchemy.exc import IntegrityError
from schoolbloc import db, app, User
from schoolbloc.users.models import Role


class BaseTestClass(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = app.test_client(use_cookies=False)
        with app.app_context():
            db.create_all()
        self._create_roles()

    def tearDown(self):
        """ Ensures that the database is emptied for next unit test """
        with app.app_context():
            db.drop_all()

    def login(self, username, password):
        login_data = {'username': username, 'password': password}
        response = self.app.post('/auth', data=json.dumps(login_data),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        return data['access_token']

    def _create_roles(self):
        for role in ('admin', 'teacher', 'student'):
            db.session.add(Role(role_type=role))

    def _create_users(self):
        db.session.add(User('student', 'student', 'student'))
        db.session.add(User('teacher', 'teacher', 'teacher'))
        db.session.add(User('admin', 'admin', 'admin'))
