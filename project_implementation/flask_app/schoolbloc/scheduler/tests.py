import unittest
from schoolbloc import app, db
from schoolbloc.teachers.models import Teacher
from schoolbloc.scheduler import scheduler

class SchedulerTests(unittest.TestCase):
    """ Testing the scheduler """

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

    def test_valid_teacher_ids(self):
        """ The selections of the scheduler are only for valid Ids """
        # make the list of teachers
        [ Teacher("first_name_%s" % i, "last_name_%s" % i) for i in range(3) ]
        scheduler.make_schedule(10)

    def test_valid_room_ids(self):
        """ It assigns only valid classroom Ids from the DB """
        pass

    def test_valid_time_ids(self):
        """ It assigns only valid time Ids from the DB """
        pass

    def test_valid_student_ids(self):
        """ It assigns only valid student Ids from the DB """
        pass

    def test_room_time_collision(self):
        """ It does not assign two classes to a room which occur at the same time """
        pass

    def test_teacher_time_collision(self):
        """ It does not assign a teacher to teach two classes which occur at the same time """
        pass

    def test_uniq_student(self):
        """It does not repeat students in a given class student list """
        pass

    def test_student_time_collision(self):
        """ It does not assign a student to two classes which occur at the same time """
        pass

    def test_max_students_in_classroom(self):
        """ It does not assign more students to the course than the maximum for the classroom """
        pass

    def test_classroom_course_soft_constraint(self):
        """ It chooses classrooms from a list of those with soft constraint to the course """
        pass

    def test_classroom_course_hard_constraint(self):
        """ It chooses only the classroom with the hard constraint to assign to the course """
        pass

    def test_classroom_course_no_constraint(self):
        """ It chooses any classroom for the course """
        pass

    def test_classroom_time_constraint(self):
        """ it does not schedule the classroom outside of the assigned time constraint """
        pass

    def test_classroom_time_no_constraint(self):
        """ It is free to assign any time to a classroom """
        pass

    def test_course_student_hard_constraint(self):
        """ It requires a student to be assigned the course """
        pass

    def test_course_student_med_constraint(self):
        """ It sets a preferred course for a student """
        pass

    def test_course_student_soft_constraint(self):
        """ It sets the course as available to the student """
        pass

    def test_course_teacher_hard_constraint(self):
        """ It requires the course for the teacher """
        pass

    def test_course_teacher_soft_constraint(self):
        """ It allows the course to be assigned to the teacher """
        pass

    def test_course_teacher_no_constraint(self):
        """ It is free to choose any course for the teacher """
        pass

    def test_course_time_start_end_constraint(self):
        """ It sets the available start and end time for a course """
        pass

    def test_course_duration_constraint(self):
        """ It sets the duration of the course """
        pass

    def test_student_group_student_constraint(self):
        """ It includes the student in the student group """
        pass

    def test_course_student_group_hard_constraint(self):
        """ It requires a student group to be assigned the course """
        pass

    def test_course_student_group_med_constraint(self):
        """ It sets a preferred course for a student group """
        pass

    def test_course_student_group_soft_constraint(self):
        """ It sets the course as available to the student group """
        pass

    def test_teacher_time_constraint(self):
        """ It doesn't schedule the teacher for classes outside the start and end time """
        pass

    def student_group_time(self):
        """ It doesn't schedule the student in the group for classes outside of the start and end time """
        pass

    

