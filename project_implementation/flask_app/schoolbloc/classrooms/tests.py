import unittest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from schoolbloc import app, db
from schoolbloc.classrooms.models import Classroom, ClassroomError

class ClassroomTests(unittest.TestCase):

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

    def test_create(self):
        c = Classroom('101')
        self.assertIsNotNone(c)
        self.assertIsNotNone(c.id)

    def test_adding_duplicate(self):
        Classroom('101')
        with self.assertRaises(ClassroomError):
            Classroom('101')

    def test_querying(self):
        Classroom('101')
        c = Classroom.query.filter_by(room_number="101").one()
        self.assertEqual(c.room_number, 101)
        with self.assertRaises(NoResultFound):
            Classroom.query.filter_by(room_number="0").one()

    def test_deleting(self):
        c = Classroom('101')
        c.delete()
        with self.assertRaises(NoResultFound):
            Classroom.query.filter_by(room_number="101").one()    

if __name__ == '__main__':
	unittest.main() 