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
        u2 = User(username='teacher', password='teacher', role_type='teacher')
        u3 = User(username='admin', password='admin', role_type='admin')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()

        # Have to re-query them after commit them so the id's properly get attached.
        # I have a feeling this is a dumb on my part here, and isn't necessary, but
        # that I am missing something
        u1 = User.query.filter_by(username='student').one()
        u2 = User.query.filter_by(username='teacher').one()
        u3 = User.query.filter_by(username='admin').one()

        # Check student getting himself
        key, _ = self.login('student', 'student')
        headers = {'Authorization': 'JWT {}'.format(key)}
        response = self.app.get('/api/users/{}'.format(u1.id), headers=headers)
        data = self.parse_response_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], u1.username)

        # Student trying to get someone else
        response = self.app.get('/api/users/{}'.format(u3.id), headers=headers)
        self.assertEqual(response.status_code, 404)

        # Teacher getting student info
        key, _ = self.login('teacher', 'teacher')
        headers = {'Authorization': 'JWT {}'.format(key)}
        response = self.app.get('/api/users/{}'.format(u1.id), headers=headers)
        data = self.parse_response_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], u1.username)

        # Admin getting teacher info
        key, _ = self.login('admin', 'admin')
        headers = {'Authorization': 'JWT {}'.format(key)}
        response = self.app.get('/api/users/{}'.format(u2.id), headers=headers)
        data = self.parse_response_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], u2.username)

    def test_update_user(self):
        pass

    def test_add_user(self):
        pass

    def test_delete_user(self):
        pass

if __name__ == '__main__':
    unittest.main()
