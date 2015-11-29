import unittest
from schoolbloc import app, db
from schoolbloc.teachers.models import Teacher
from schoolbloc.classrooms.models import Classroom
from schoolbloc.classrooms.models import ClassroomsCourse
from schoolbloc.courses.models import Course
from schoolbloc.scheduler.scheduler import Scheduler
from schoolbloc.students.models import Student
from schoolbloc.scheduled_classes.models import ScheduledClass
from schoolbloc.scheduled_classes.models import ScheduledClassesStudent

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

    def gen_test_data(self):
        # Make all the DB facts we need for our tests
        [ Teacher("first_name_%s" % i, "last_name_%s" % i) for i in range(3) ]
        [ Classroom(i+1) for i in range(3) ]
        [ Course("course_%s" % i) for i in range(3) ]
        [ Student("first_name_%s" % i, "last_name_%s" % i) for i in range(3) ]

    def test_generate_schedule(self):
        """ It creates 10 scheduled classes """
        self.gen_test_data()
        
        scheduler = Scheduler()
        scheduler.make_schedule()
        self.assertTrue(len(ScheduledClass.query.all()) == 10)

    def test_valid_teacher_ids(self):
        """ The selections of the scheduler are only for valid Ids """
        self.gen_test_data()

        scheduler = Scheduler()
        scheduler.make_schedule()
        # now loop through the scheduled classes and make sure all the teachers are valid
        teacher_ids = [ t.id for t in Teacher.query.all() ]
        for c in ScheduledClass.query.all():
            self.assertIn(c.teacher_id, teacher_ids)

    def test_valid_room_ids(self):
        """ It assigns only valid classroom Ids from the DB """
        self.gen_test_data()

        scheduler = Scheduler()
        scheduler.make_schedule()
        # now loop through the scheduled classes and make sure all the teachers are valid
        room_ids = [ t.id for t in Classroom.query.all() ]
        for c in ScheduledClass.query.all():
            self.assertIn(c.classroom_id, room_ids)


    def test_valid_student_ids(self):
        """ It assigns only valid student Ids from the DB """
        self.gen_test_data()

        scheduler = Scheduler()
        scheduler.make_schedule()
        # now loop through the scheduled classes and make sure all the teachers are valid
        student_ids = [ s.id for s in Student.query.all() ]
        for c in ScheduledClass.query.all():
            for stud in c.students:
                self.assertIn(stud.id, student_ids)


    def test_class_duration_default(self):
        """ It sets the duration of all classes to the default value when a course.duration
            Is not set """
        self.gen_test_data()

        scheduler = Scheduler(class_duration=60)
        scheduler.make_schedule()
        for c in ScheduledClass.query.all():
            self.assertEqual((c.end_time - c.start_time), 60)

    def test_class_duration(self):
        """ It sets the duration of a class to the value in the course when it is not None """
        self.gen_test_data()

        course = Course("course name", duration=60)
        scheduler = Scheduler(class_duration=50)
        scheduler.make_schedule()
        for c in ScheduledClass.query.all():
            if c.course_id == course.id:
                self.assertEqual((c.end_time - c.start_time), 60)
            else:
                self.assertEqual((c.end_time - c.start_time), 50)

    def test_lunch_period(self):
        """ It doesn't schedule any classes during the lunch break """
        self.gen_test_data()

        scheduler = Scheduler(lunch_start=1150, lunch_end=1300)
        scheduler.make_schedule()
        for c in ScheduledClass.query.all():
            self.assertTrue( (c.start_time <= scheduler.lunch_start and c.end_time <= scheduler.lunch_start) or 
                             (c.start_time >= scheduler.lunch_end and c.end_time >= scheduler.lunch_end) )

    # def test_break_periods(self):
    #     """ It doesn't schedule the start of a class within 'break_length' minutes of the 
    #         end of the previous class for the same room, teacher, or student """
    #     # make sure there are possible room, teacher, and student colisions
    #     teacher1 = Teacher("teacher1 first", "teacher1 last")
    #     teacher2 = Teacher("teacher2 first", "teacher2 last")
    #     course1 = Course("course1 name")
    #     course2 = Course("course2 name")
    #     course3 = Course("course3 name")
    #     course4 = Course("course4 name")
    #     room1 = Classroom(101)
    #     room2 = Classroom(101)
    #     room3 = Classroom(103)

    #     # teacher1 can only teacher course1 and course 2
    #     CoursesTeacher(teacher1.id, course1.id)
    #     CoursesTeacher(teacher1.id, course2.id)

        

    #     # student1 must take course1 and course

    #     scheduler = Scheduler(break_length=10)
    #     scheduler.make_schedule()
        
    
    def test_room_time_collision(self):
        """ It does not assign two classes to a room which occur at the same time """
        [ Teacher("teacher_f_%s" % i, "teacher_l_%s" % i) for i in range(3) ]
        [ Student("student_f_%s" % i, "student_l_%s" % i) for i in range(3) ]
        
        course1 = Course("course1 name")
        course2 = Course("course2 name")
        room1 = Classroom(101)

        # course1 and course2 must be in room1
        ClassroomsCourse(room1.id, course1.id)
        ClassroomsCourse(room1.id, course2.id)

        # make sure there is only two time slots per day
        scheduler = Scheduler(day_start_time=800, break_length=1, 
                              day_end_time=909, class_duration=9,
                              lunch_start=809, lunch_end=900, class_count=2)
        scheduler.make_schedule()

        for class1 in ScheduledClass.query.filter_by(course_id=course1.id):
            for class2 in ScheduledClass.query.filter_by(course_id=course2.id):
                self.assertNotEqual(class1.start_time, class2.start_time)
                self.assertNotEqual(class1.end_time, class2.end_time)

    def test_teacher_time_collision(self):
        """ It does not assign a teacher to teach two classes which occur at the same time """
        [ Room(i + 100) for i in range(3) ]
        [ Student("student_f_%s" % i, "student_l_%s" % i) for i in range(3) ]
        
        course1 = Course("course1 name")
        course2 = Course("course2 name")
        teacher1 = Teacher("first", "last")

        # course1 and course2 must be taught by teacher1
        CoursesTeacher(teacher1.id, course1.id)
        CoursesTeacher(teacher1.id, course2.id)

        # make sure there is only two time slots per day
        scheduler = Scheduler(day_start_time=800, break_length=1, 
                              day_end_time=909, class_duration=9,
                              lunch_start=809, lunch_end=900, class_count=2)
        scheduler.make_schedule()

        for class1 in ScheduledClass.query.filter_by(course_id=course1.id):
            for class2 in ScheduledClass.query.filter_by(course_id=course2.id):
                self.assertNotEqual(class1.start_time, class2.start_time)
                self.assertNotEqual(class1.end_time, class2.end_time)

    def test_uniq_student(self):
        """It does not repeat students in a given class student list """
        self.gen_test_data()
        scheduler = Scheduler()
        scheduler.make_schedule()

        for c in ScheduledClass.query.all():
            stud_ids = []
            for stud in c.students:
                self.assertNotIn(stud.id, stud_ids)
                stud_ids.append(stud.id)

    def test_student_time_collision(self):
        """ It does not assign a student to two classes which occur at the same time """
        [ Room(i + 100) for i in range(3) ]
        [ Teacher("teacher_f_%s" % i, "teacher_l_%s" % i) for i in range(3) ]
        
        course1 = Course("course1 name")
        course2 = Course("course2 name")
        student1 = Student("first", "last")

        # student1 must take course1 and course2 must be taught by teacher1
        CoursesTeacher(teacher1.id, course1.id)
        CoursesTeacher(teacher1.id, course2.id)

        # make sure there is only two time slots per day
        scheduler = Scheduler(day_start_time=800, break_length=1, 
                              day_end_time=909, class_duration=9,
                              lunch_start=809, lunch_end=900, class_count=2)
        scheduler.make_schedule()

        for class1 in ScheduledClass.query.filter_by(course_id=course1.id):
            for class2 in ScheduledClass.query.filter_by(course_id=course2.id):
                self.assertNotEqual(class1.start_time, class2.start_time)
                self.assertNotEqual(class1.end_time, class2.end_time)

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

    

