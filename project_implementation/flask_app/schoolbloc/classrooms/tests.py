import unittest
from sqlalchemy.orm.exc import NoResultFound
from schoolbloc import app, db
from schoolbloc.classrooms.models import Classroom


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
        c = Classroom(room_number=101)
        db.session.add(c)
        db.session.commit()
        self.assertIsNotNone(c)
        self.assertIsNotNone(c.id)

    # def test_adding_duplicate(self):
    #     c = Classroom(room_number=101)
    #     db.session.add(c)
    #     db.session.commit()
    #     with self.assertRaises(ClassroomError):
    #         dup = Classroom(room_number=101)
    #         db.session.add(dup)
    #         db.session.commit()

    def test_querying(self):
        c = Classroom(room_number=101)
        db.session.add(c)
        db.session.commit()
        c = Classroom.query.filter_by(room_number=101).one()
        self.assertEqual(c.room_number, 101)
        with self.assertRaises(NoResultFound):
            Classroom.query.filter_by(room_number=0).one()

    # def test_deleting(self):
    #     c = Classroom(room_number=101)
    #     db.session.add(c)
    #     db.session.commit()
    #     c.delete()
    #     with self.assertRaises(NoResultFound):
    #         Classroom.query.filter_by(room_number=101).one()    


if __name__ == '__main__':
    unittest.main()