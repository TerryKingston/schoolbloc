import unittest
from schoolbloc import app, db
from schoolbloc.users.models import User, Role
from schoolbloc.scheduler.models import *
from schoolbloc.scheduler.scheduler import Scheduler


class SchedulerTests(unittest.TestCase):
    """ Testing the scheduler """

    def setUp(self):
        """ Uses an in memory sqlite database for testing """
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.init_app(app)
        with app.app_context():
            db.create_all()

        db.session.add(Role(role_type='admin'))
        db.session.add(Role(role_type='teacher'))
        db.session.add(Role(role_type='student'))
        db.session.commit()
        
    def tearDown(self):
        """ Ensures that the database is emptied for next unit test """
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.init_app(app)
        with app.app_context():
            db.drop_all()

    def gen_test_data(self):

        # Make all the DB facts we need for our tests
        t_user_list = [ User('t_user_%s' % i, 'password', 'teacher') for i in range(10)]
        for u in t_user_list: db.session.add(u)
        db.session.flush()

        teach_list = [ Teacher(first_name="first_name_%s" % i, 
                               last_name="last_name_%s" % i, 
                               user_id=t_user_list[i].id) for i in range(10) ]

        for t in teach_list: db.session.add(t)

        room_list = [ Classroom(room_number=i+1) for i in range(10) ]
        for r in room_list: db.session.add(r) 

        # course_list = [ Course(name="course_%s" % i) for i in range(10) ]
        sg_course =  Course(name="SG reqired course", 
                            duration=82, 
                            min_student_count=0,
                            max_student_count=30) 
        db.session.add(sg_course)
        # for c in course_list: db.session.add(c)

        s_user_list = [ User('s_user_%s' % i, 'password', 'student') for i in range(10)]
        for u in s_user_list: db.session.add(u)
        db.session.flush()

        stud_list = [ Student(first_name="first_name_%s" % i, 
                              last_name="last_name_%s" % i, 
                              user_id=s_user_list[i].id) for i in range(10) ]
        for s in stud_list: db.session.add(s)
        db.session.flush()

        stud_grp = StudentGroup(name="Student Group 1")
        db.session.add(stud_grp)
        db.session.flush()
        for s in stud_list:
            db.session.add(StudentsStudentGroup(student_id=s.id, student_group_id=stud_grp.id))

        db.session.add(CoursesStudentGroup(student_group_id=stud_grp.id, course_id=sg_course.id))
        # db.session.add(CoursesStudentGroup(student_group_id=stud_grp.id, course_id=course_list[1].id))

        db.session.commit()

    def test_valid_teacher_ids(self):
        """ The selections of the scheduler are only for valid Ids """
        self.gen_test_data()

        scheduler = Scheduler(class_count=20)
        scheduler.make_schedule()
        # now loop through the scheduled classes and make sure all the teachers are valid
        teacher_ids = [ t.id for t in Teacher.query.all() ]
        for c in ScheduledClass.query.all():
            self.assertIn(c.teacher_id, teacher_ids)

    # def test_valid_room_ids(self):
    #     """ It assigns only valid classroom Ids from the DB """
    #     self.gen_test_data()

    #     scheduler = Scheduler()
    #     scheduler.make_schedule()
    #     # now loop through the scheduled classes and make sure all the teachers are valid
    #     room_ids = [ t.id for t in Classroom.query.all() ]
    #     for c in ScheduledClass.query.all():
    #         self.assertIn(c.classroom_id, room_ids)


    # def test_valid_student_ids(self):
    #     """ It assigns only valid student Ids from the DB """
    #     self.gen_test_data()

    #     scheduler = Scheduler()
    #     scheduler.make_schedule()
    #     # now loop through the scheduled classes and make sure all the teachers are valid
    #     student_ids = [ s.id for s in Student.query.all() ]
    #     for c in ScheduledClass.query.all():
    #         for stud in c.students:
    #             self.assertIn(stud.id, student_ids)


    # def test_class_duration_default(self):
    #     """ It sets the duration of all classes to the default value when a course.duration
    #         Is not set """
    #     self.gen_test_data()

    #     scheduler = Scheduler(class_duration=60)
    #     scheduler.make_schedule()
    #     for c in ScheduledClass.query.all():
    #         self.assertEqual((c.end_time - c.start_time), 60)

    # def test_class_duration(self):
    #     """ It sets the duration of a class to the value in the course when it is not None """
    #     self.gen_test_data()

    #     course = Course(name="course name", duration=60)
    #     db.session.add(course)
    #     db.session.commit()
    #     scheduler = Scheduler(class_duration=50)
    #     scheduler.make_schedule()
    #     for c in ScheduledClass.query.all():
    #         if c.course_id == course.id:
    #             self.assertEqual((c.end_time - c.start_time), 60)
    #         else:
    #             self.assertEqual((c.end_time - c.start_time), 50)

    # def test_lunch_period(self):
    #     """ It doesn't schedule any classes during the lunch break """
    #     self.gen_test_data()

    #     scheduler = Scheduler(lunch_start=1150, lunch_end=1300)
    #     scheduler.make_schedule()
    #     for c in ScheduledClass.query.all():
    #         self.assertTrue( (c.start_time <= scheduler.lunch_start and c.end_time <= scheduler.lunch_start) or 
    #                          (c.start_time >= scheduler.lunch_end and c.end_time >= scheduler.lunch_end) )

    # def test_break_periods(self):
    #     """ It doesn't schedule the start of a class within 'break_length' minutes of the 
    #         end of the previous class for the same room, teacher, or student """
    #     # make sure there are possible room, teacher, and student colisions
    #     teacher1 = Teacher(first_name="teacher1 first", "teacher1 last")
    #     teacher2 = Teacher(first_name="teacher2 first", "teacher2 last")
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
        
    
    # def test_room_time_collision(self):
    #     """ It does not assign two classes to a room which occur at the same time """

    #     t_user_list = [ User('t_user_%s' % i, 'password', 'teacher') for i in range(3)]
    #     for u in t_user_list: db.session.add(u)
    #     db.session.commit()

    #     teach_list = [ Teacher(first_name="teacher_f_%s" % i, last_name="teacher_l_%s" % i, user_id=t_user_list[i].id) for i in range(3) ]
    #     for t in teach_list: db.session.add(t)

    #     s_user_list = [ User('s_user_%s' % i, 'password', 'teacher') for i in range(3)]
    #     for u in s_user_list: db.session.add(u)
    #     db.session.commit()

    #     stud_list = [ Student(first_name="student_f_%s" % i, last_name="student_l_%s" % i, user_id=s_user_list[i].id) for i in range(3) ]
    #     for s in stud_list: db.session.add(s)
    #     db.session.commit()
        
    #     course1 = Course(name="course1 name")
    #     course2 = Course(name="course2 name")
    #     room1 = Classroom(room_number=101)
    #     db.session.add(course1)
    #     db.session.add(course2)
    #     db.session.add(room1)
    #     db.session.commit()

    #     # course1 and course2 must be in room1
    #     cc1 = ClassroomsCourse(classroom_id=room1.id, course_id=course1.id)
    #     cc2 = ClassroomsCourse(classroom_id=room1.id, course_id=course2.id)
    #     db.session.add(cc1)
    #     db.session.add(cc2)
    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=2)
    #     scheduler.make_schedule()

    #     for class1 in ScheduledClass.query.filter_by(course_id=course1.id):
    #         for class2 in ScheduledClass.query.filter_by(course_id=course2.id):
    #             self.assertNotEqual(class1.start_time, class2.start_time)
    #             self.assertNotEqual(class1.end_time, class2.end_time)

    # def test_teacher_time_collision(self):
    #     """ It does not assign a teacher to teach two classes which occur at the same time """
        
    #     room_list = [ Classroom(room_number=i + 100) for i in range(3) ]
    #     for r in room_list: db.session.add(r)
        
    #     s_user_list = [ User('s_user_%s' % i, 'password', 'teacher') for i in range(3)]
    #     for u in s_user_list: db.session.add(u)
    #     db.session.commit()

    #     stud_list = [ Student(first_name="student_f_%s" % i, last_name="student_l_%s" % i, user_id=s_user_list[i].id) for i in range(3) ]
    #     for s in stud_list: db.session.add(s)

    #     course1 = Course(name="course1 name")
    #     course2 = Course(name="course2 name")
    #     db.session.add(course1)
    #     db.session.add(course2)

    #     user = User("t_user_name", "password", "teacher")
    #     db.session.add(user)
    #     db.session.commit()

    #     teacher1 = Teacher(first_name="first", last_name="last", user_id=user.id)
    #     db.session.add(teacher1)
    #     db.session.commit()

    #     # course1 and course2 must be taught by teacher1
    #     ct1 = CoursesTeacher(teacher_id=teacher1.id, course_id=course1.id)
    #     ct2 = CoursesTeacher(teacher_id=teacher1.id, course_id=course2.id)
    #     db.session.add(ct1)
    #     db.session.add(ct2)
    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=2)
    #     scheduler.make_schedule()

    #     for class1 in ScheduledClass.query.filter_by(course_id=course1.id):
    #         for class2 in ScheduledClass.query.filter_by(course_id=course2.id):
    #             self.assertNotEqual(class1.start_time, class2.start_time)
    #             self.assertNotEqual(class1.end_time, class2.end_time)

    # def test_uniq_student(self):
    #     """It does not repeat students in a given class student list """
    #     self.gen_test_data()
    #     scheduler = Scheduler()
    #     scheduler.make_schedule()

    #     for c in ScheduledClass.query.all():
    #         stud_ids = []
    #         for stud in c.students:
    #             self.assertNotIn(stud.id, stud_ids)
    #             stud_ids.append(stud.id)

    # def test_student_time_collision(self):
    #     """ It does not assign a student to two classes which occur at the same time """
    #     room_list = [ Classroom(room_number=i + 100) for i in range(3) ]
    #     for r in room_list: db.session.add(r)

    #     t_user_list = [ User('t_user_%s' % i, 'password', 'teacher') for i in range(3)]
    #     for u in t_user_list: db.session.add(u)
    #     db.session.commit()

    #     teach_list = [ Teacher(first_name="teacher_f_%s" % i, last_name="teacher_l_%s" % i, user_id=t_user_list[i].id) for i in range(3) ]
    #     for t in teach_list: db.session.add(t)

    #     course1 = Course(name="course1 name")
    #     course2 = Course(name="course2 name")
    #     db.session.add(course1)
    #     db.session.add(course2)

    #     s_user = User("s_user_name", "password", "student")
    #     db.session.add(s_user)
    #     db.session.commit()

    #     student1 = Student(first_name="first", last_name="last", user_id=s_user.id)
    #     db.session.add(student1)
    #     db.session.commit()

    #     # student1 must take course1 and course2 
    #     ct1 = CoursesStudent(student_id=student1.id, course_id=course1.id)
    #     ct2 = CoursesStudent(student_id=student1.id, course_id=course2.id)
    #     db.session.add(ct1)
    #     db.session.add(ct2)
    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=2)
    #     scheduler.make_schedule()

    #     for class1 in ScheduledClass.query.filter_by(course_id=course1.id):
    #         for class2 in ScheduledClass.query.filter_by(course_id=course2.id):
    #             self.assertNotEqual(class1.start_time, class2.start_time)
    #             self.assertNotEqual(class1.end_time, class2.end_time)

    # def test_max_students_in_classroom(self):
    #     """ It does not assign more students to the course than the maximum for the classroom """
    #     pass

    # def test_classroom_course_soft_constraint(self):
    #     """ It chooses classrooms from a list of those with soft constraint to the course """
    #     pass

    # def test_classroom_course_hard_constraint(self):
    #     """ It chooses only the classroom with the hard constraint to assign to the course """
    #     pass

    # def test_classroom_course_no_constraint(self):
    #     """ It chooses any classroom for the course """
    #     pass

    # def test_classroom_time_constraint(self):
    #     """ it does not schedule the classroom outside of the assigned time constraint """
    #     pass

    # def test_classroom_time_no_constraint(self):
    #     """ It is free to assign any time to a classroom """
    #     pass

    # def test_course_student_hard_constraint(self):
    #     """ It requires a student to be assigned the course """
    #     pass

    # def test_course_student_med_constraint(self):
    #     """ It sets a preferred course for a student """
    #     pass

    # def test_course_student_soft_constraint(self):
    #     """ It sets the course as available to the student """
    #     pass

    # def test_course_teacher_hard_constraint(self):
    #     """ It requires the course for the teacher """
    #     pass

    # def test_course_teacher_soft_constraint(self):
    #     """ It allows the course to be assigned to the teacher """
    #     pass

    # def test_course_teacher_no_constraint(self):
    #     """ It is free to choose any course for the teacher """
    #     pass

    # def test_course_time_start_end_constraint(self):
    #     """ It sets the available start and end time for a course """
    #     pass

    # def test_course_duration_constraint(self):
    #     """ It sets the duration of the course """
    #     pass

    # def test_student_group_student_constraint(self):
    #     """ It includes the student in the student group """
    #     pass

    # def test_course_student_group_hard_constraint(self):
    #     """ It requires a student group to be assigned the course """
    #     pass

    # def test_course_student_group_med_constraint(self):
    #     """ It sets a preferred course for a student group """
    #     pass

    # def test_course_student_group_soft_constraint(self):
    #     """ It sets the course as available to the student group """
    #     pass

    # def test_teacher_time_constraint(self):
    #     """ It doesn't schedule the teacher for classes outside the start and end time """
    #     pass

    # def student_group_time(self):
    #     """ It doesn't schedule the student in the group for classes outside of the start and end time """
    #     pass

    

