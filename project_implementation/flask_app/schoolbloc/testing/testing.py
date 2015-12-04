import unittest
from flask import json
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

    def parse_response_json(self, response):
        # God knows why, but for some reason, sometimes, the first json.loads
        # returns a string instead of a dict/list/whatever. This is a dumb fix
        data = json.loads(response.get_data(as_text=True))
        if isinstance(data, str):
            data = json.loads(data)
        return data

    def login(self, username, password):
        login_data = {'username': username, 'password': password}
        response = self.app.post('/auth', data=json.dumps(login_data),
                                 content_type='application/json')
        data = self.parse_response_json(response)
        try:
            return data['access_token'], response.status_code
        except KeyError:
            return data, response.status_code

    def _create_roles(self):
        for role in ('admin', 'teacher', 'student'):
            db.session.add(Role(role_type=role))

