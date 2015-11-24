import unittest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from schoolbloc import app, db
from schoolbloc.users.models import Role, RoleError, User


class UserRoleTests(unittest.TestCase):
    """ Unit tests for Roles and Users """

    def setUp(self):
        """ Uses an in memory sqlite database for testing """
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """ Ensures that the database is emptied for next unit test """
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.init_app(app)
        with app.app_context():
            db.drop_all()

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


if __name__ == '__main__':
    unittest.main()
