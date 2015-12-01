import unittest
import json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import schoolbloc
from schoolbloc.users.models import Role, RoleError, User


class UserRoleTests(unittest.TestCase):
    """ Unit tests for Roles and Users """

    def setUp(self):
        """ Uses an in memory sqlite database for testing """
        schoolbloc.app.config.from_object('config')
        schoolbloc.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = schoolbloc.app.test_client(use_cookies=False)
        with schoolbloc.app.app_context():
            schoolbloc.db.create_all()

    def tearDown(self):
        """ Ensures that the database is emptied for next unit test """
        with schoolbloc.app.app_context():
            schoolbloc.db.drop_all()

    def get_login_token(self, role):
        Role(role)
        User('user', 'user', role)
        a = self.app.post('/auth', data=json.dumps({'username': 'user', 'password': 'user'}),
                          content_type='application/json')
        data = json.loads(a.get_data(as_text=True))
        return data['access_token']

    def test_adding_role(self):
        r = Role('admin')
        self.assertEqual(r.role_type, 'admin')

    def test_adding_duplicate_role(self):
        Role('admin')
        with self.assertRaises(RoleError):
            Role('admin')

    def test_querying_role(self):
        Role('admin')
        r = Role.query.filter_by(role_type='admin').one()
        self.assertEqual(r.role_type, 'admin')
        with self.assertRaises(NoResultFound):
            Role.query.filter_by(role_type='banana').one()

    def test_deleting_role(self):
        r = Role('admin')
        r.delete()
        with self.assertRaises(NoResultFound):
            Role.query.filter_by(role_type='admin').one()

    def test_deleting_non_empty_role(self):
        r = Role('admin')
        User('dumbldoor', 'wingardium', 'admin')
        with self.assertRaises(IntegrityError):
            r.delete()

    def test_login(self):
        self.get_login_token('student')

if __name__ == '__main__':
    unittest.main()
