import unittest
from schoolbloc import db
from schoolbloc.testing.testing import BaseTestClass
from schoolbloc.users.models import User


class UserTests(BaseTestClass):
    """ Unit tests for Roles and Users """

    def test_login(self):
        db.session.add(User('student', 'student', 'student'))
        self.login('student', 'student')

if __name__ == '__main__':
    unittest.main()
