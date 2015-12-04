import unittest
from schoolbloc import User, db
from schoolbloc.testing.testing import BaseTestClass


class UserTests(BaseTestClass):
    """ Unit tests for Roles and Users """

    def test_valid_login(self):
        db.session.add(User(username='student', password='student', role_type='student'))
        key, status_code = self.login('student', 'student')
        self.assertEqual(status_code, 200)

    def test_invalid_login(self):
        db.session.add(User(username='student', password='student', role_type='student'))
        key, status_code = self.login('student', 'bad_pw')
        self.assertEqual(status_code, 401)

    def test_get_user(self):
        # setup users
        u1 = User(username='student', password='student', role_type='student')
        db.session.add(u1)
        db.session.commit()

        # Get jwt auth key
        key, _ = self.login('student', 'student')

        # Perform restful get
        headers = {'Authorization': 'JWT {}'.format(key)}
        response = self.app.get('/api/users/{}'.format(u1.id), headers=headers,
                                content_type='application/json')
        data = self.parse_response_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], u1.username)

        # TODO students can get only themselves, admins and teachers can get
        #      anyone

if __name__ == '__main__':
    unittest.main()
