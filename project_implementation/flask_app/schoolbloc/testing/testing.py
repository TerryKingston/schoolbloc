import unittest
import schoolbloc


class BaseTestClass(unittest.TestCase):
    def setUp(self):
        schoolbloc.app.config.from_object('config')
        schoolbloc.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = schoolbloc.app.test_client(use_cookies=False)
        with schoolbloc.app.app_context():
            schoolbloc.db.create_all()

    def tearDown(self):
        """ Ensures that the database is emptied for next unit test """
        with schoolbloc.app.app_context():
            schoolbloc.db.drop_all()

    def login(self, username, password):
        login_data = {'username': username, 'password': password}
        response = self.app.post('/auth', data=json.dumps(login_data),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        return data['access_token']

    def create_users(self):
        for role in ('admin', 'teacher', 'student'):
            db.session.add(Role(role))
        # TODO
