import unittest
from schoolbloc import app, db
from schoolbloc.users.models import User, Role
from schoolbloc.scheduler.models import *
from schoolbloc.scheduler.scheduler import Scheduler, SchedulerNoSolution
from random import *



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

    def gen_students(self, n):
        """ returns n students in a list after saving them to the DB """
        s_user_list = [ User('s_user_%s' % random(), 'password', 'teacher') 
                        for i in range(n)]
        for u in s_user_list: db.session.add(u)
        db.session.flush()

        stud_list = [ Student(first_name="student_f_%s" % i, 
                              last_name="student_l_%s" % i, 
                              user_id=s_user_list[i].id) 
                      for i in range(n) ]

        for s in stud_list: db.session.add(s)
        db.session.commit()
        return stud_list

    def gen_teachers(self, n, avail_start_time=None, avail_end_time=None):
        t_user_list = [ User('t_user_%s' % random(), 'password', 'teacher') for i in range(n)]
        for u in t_user_list: db.session.add(u)
        db.session.flush()

        teach_list = [ Teacher(first_name="teacher_f_%s" % i, 
                               last_name="teacher_l_%s" % i, 
                               user_id=t_user_list[i].id,
                               avail_start_time=avail_start_time,
                               avail_end_time=avail_end_time) 
                       for i in range(n) ]

        for t in teach_list: db.session.add(t)
        db.session.commit()
        return teach_list

    def gen_classrooms(self, n, max_student_count=None, avail_start_time=None, avail_end_time=None):
        rooms = [ Classroom(room_number=randint(0, 1000000), 
                            max_student_count=max_student_count,
                            avail_start_time=avail_start_time,
                            avail_end_time=avail_end_time) 
                  for i in range(n) ]

        for r in rooms:
            db.session.add(r)
        db.session.commit()
        return rooms

    def gen_courses(self, n, max_student_count=None, avail_start_time=None, avail_end_time=None):
        courses = [ Course(name="course {}".format(randint(0, 1000000)),
                           max_student_count=max_student_count,
                           avail_start_time=avail_start_time,
                           avail_end_time=avail_end_time) 
                    for i in range(n) ]

        for r in courses:
            db.session.add(r)
        db.session.commit()
        return courses

    def gen_subjects(self, n, max_student_count=None):
        subjects = [ Subject(name="subject {}".format(randint(0, 1000000))) for i in range(n) ]

        for r in subjects:
            db.session.add(r)
        db.session.commit()
        return subjects

    def gen_student_groups(self, n):
        student_groups = [ StudentGroup(name="student group {}".format(randint(0, 1000000))) for i in range(n) ]

        for r in student_groups:
            db.session.add(r)
        db.session.commit()
        return student_groups

    def gen_test_data(self):

        # Make all the DB facts we need for our tests
        self.gen_teachers(10)
        stud_list = self.gen_students(10)
        self.gen_classrooms(10)

        # course_list = [ Course(name="course_%s" % i) for i in range(10) ]
        course =  Course(name="SG reqired course") 
        db.session.add(course)
        # for c in course_list: db.session.add(c)

        stud_grp = StudentGroup(name="Student Group 1")
        db.session.add(stud_grp)
        db.session.flush()

        for s in stud_list:
            db.session.add(StudentsStudentGroup(student_id=s.id, student_group_id=stud_grp.id))

        db.session.add(CoursesStudentGroup(student_group_id=stud_grp.id, course_id=course.id))
        # db.session.add(CoursesStudentGroup(student_group_id=stud_grp.id, course_id=course_list[1].id))

        db.session.commit()

    def test_valid_teacher_ids(self):
        """ The selections of the scheduler are only for valid Ids """
        self.gen_test_data()

        scheduler = Scheduler(class_count=20)
        scheduler.make_schedule()
        # now loop through the scheduled classes and make sure all the teachers are valid
        teacher_ids = [ t.id for t in Teacher.query.all() ]

        classes = ScheduledClass.query.all()
        self.assertNotEqual(len(classes), 0)
        for c in classes:
            self.assertIn(c.teacher_id, teacher_ids)

    # def test_valid_room_ids(self):
    #     """ It assigns only valid classroom Ids from the DB """
    #     self.gen_test_data()

    #     scheduler = Scheduler()
    #     scheduler.make_schedule()
    #     # now loop through the scheduled classes and make sure all the teachers are valid
    #     room_ids = [ t.id for t in Classroom.query.all() ]

    #     classes = ScheduledClass.query.all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         self.assertIn(c.classroom_id, room_ids)


    # def test_valid_student_ids(self):
    #     """ It assigns only valid student Ids from the DB """
    #     self.gen_test_data()

    #     scheduler = Scheduler()
    #     scheduler.make_schedule()
    #     # now loop through the scheduled classes and make sure all the teachers are valid
    #     student_ids = [ s.id for s in Student.query.all() ]

    #     classes = ScheduledClass.query.all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         for stud in c.students:
    #             self.assertIn(stud.id, student_ids)


    # def test_class_duration_default(self):
    #     """ It sets the duration of all classes to the default value when a course.duration
    #         Is not set """
    #     self.gen_test_data()

    #     scheduler = Scheduler(class_duration=60)
    #     scheduler.make_schedule()

    #     classes = ScheduledClass.query.all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         self.assertEqual((c.end_time - c.start_time), 60)

    # def test_class_duration(self):
    #     """ It sets the duration of a class to the value in the course when it is not None """
    #     self.gen_test_data()

    #     course = Course(name="course name", duration=60)
    #     db.session.add(course)
    #     db.session.commit()
    #     scheduler = Scheduler(class_duration=50)
    #     scheduler.make_schedule()

    #     classes = ScheduledClass.query.all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         if c.course_id == course.id:
    #             self.assertEqual((c.end_time - c.start_time), 60)
    #         else:
    #             self.assertEqual((c.end_time - c.start_time), 50)

    # def test_lunch_period(self):
    #     """ It doesn't schedule any classes during the lunch break """
    #     self.gen_test_data()

    #     scheduler = Scheduler(lunch_start=1150, lunch_end=1300)
    #     scheduler.make_schedule()

    #     classes = ScheduledClass.query.all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         self.assertTrue( (c.start_time <= scheduler.lunch_start and c.end_time <= scheduler.lunch_start) or 
    #                          (c.start_time >= scheduler.lunch_end and c.end_time >= scheduler.lunch_end) )

    # def test_break_periods(self):
    #     """ It doesn't schedule the start of a class within 'break_length' minutes of the 
    #         end of the previous class for the same room, teacher, or student """
    #     # TODO
        
    
    # def test_room_time_collision(self):
    #     """ It does not assign two classes to a room which occur at the same time """

    #     teach_list = self.gen_teachers(3)
    #     stud_list1 = self.gen_students(3)
    #     stud_list2 = self.gen_students(3)

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

    #     # add some requirements to students for class1 and class2 so we 
    #     # get some to show up in the schedule
    #     for stud in stud_list1:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course1.id))
    #     for stud in stud_list2:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course2.id))

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=2)
    #     scheduler.make_schedule()

    #     class1s = ScheduledClass.query.filter_by(course_id=course1.id).all()
    #     class2s = ScheduledClass.query.filter_by(course_id=course2.id).all()

    #     self.assertNotEqual(len(class1s), 0)
    #     self.assertNotEqual(len(class2s), 0)

    #     for c1 in class1s:
    #         self.assertEqual(c1.classroom_id, room1.id)
    #         for c2 in class2s:
    #             self.assertEqual(c2.classroom_id, room1.id)
    #             self.assertNotEqual(c1.start_time, c2.start_time)
    #             self.assertNotEqual(c1.end_time, c2.end_time)

    # def test_teacher_time_collision(self):
    #     """ It does not assign a teacher to teach two classes which occur at the same time """
        
    #     room_list = [ Classroom(room_number=i + 100) for i in range(3) ]
    #     for r in room_list: db.session.add(r)
        
    #     stud_list1 = self.gen_students(3)
    #     stud_list2 = self.gen_students(3)
    #     teacher1 = self.gen_teachers(1)[0]

    #     course1 = Course(name="course1 name")
    #     course2 = Course(name="course2 name")
    #     db.session.add(course1)
    #     db.session.add(course2)
    #     db.session.flush()

    #     # course1 and course2 must be taught by teacher1
    #     ct1 = CoursesTeacher(teacher_id=teacher1.id, course_id=course1.id)
    #     ct2 = CoursesTeacher(teacher_id=teacher1.id, course_id=course2.id)
    #     db.session.add(ct1)
    #     db.session.add(ct2)
    #     db.session.commit()

    #     # add some requirements to students for class1 and class2 so we 
    #     # get some to show up in the schedule
    #     for stud in stud_list1:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course1.id))
    #     for stud in stud_list2:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course2.id))

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     class1s = ScheduledClass.query.filter_by(course_id=course1.id).all()
    #     class2s = ScheduledClass.query.filter_by(course_id=course2.id).all()

    #     self.assertNotEqual(len(class1s), 0)
    #     self.assertNotEqual(len(class2s), 0)

    #     for c1 in class1s:
    #         self.assertEqual(c1.teacher_id, teacher1.id)
    #         for c2 in class2s:
    #             self.assertEqual(c2.teacher_id, teacher1.id)
    #             self.assertNotEqual(c1.start_time, c2.start_time)
    #             self.assertNotEqual(c1.end_time, c2.end_time)

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

    #     teach_list = self.gen_teachers(3)

    #     course1 = Course(name="course1 name")
    #     course2 = Course(name="course2 name")
    #     db.session.add(course1)
    #     db.session.add(course2)

    #     student1 = self.gen_students(1)[0]

    #     # student1 must take course1 and course2 
    #     ct1 = CoursesStudent(student_id=student1.id, course_id=course1.id)
    #     ct2 = CoursesStudent(student_id=student1.id, course_id=course2.id)
    #     db.session.add(ct1)
    #     db.session.add(ct2)
    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     class1s = ScheduledClass.query.filter_by(course_id=course1.id).all()
    #     class2s = ScheduledClass.query.filter_by(course_id=course2.id).all()
    #     self.assertNotEqual(len(class1s), 0)
    #     self.assertNotEqual(len(class2s), 0)

    #     for c1 in class1s:
    #         for c2 in class2s:
    #             self.assertNotEqual(c1.start_time, c2.start_time)
    #             self.assertNotEqual(c1.end_time, c2.end_time)

    # def test_max_students_in_classroom(self):
    #     """ It does not assign more students to the course than the maximum for the classroom """
        
    #     self.gen_teachers(5)
    #     stud_list = self.gen_students(20)

    #     room1 = self.gen_classrooms(1, max_student_count=15)[0]
    #     room2 = self.gen_classrooms(1, max_student_count=10)[0]
    #     course = self.gen_courses(1)[0]

    #     db.session.add(ClassroomsCourse(course_id=course.id, classroom_id=room1.id))
    #     db.session.add(ClassroomsCourse(course_id=course.id, classroom_id=room2.id))

    #     for stud in stud_list:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course.id))

    #     db.session.commit()

    #     # make sure there is only one time slot per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=900, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     class1s = ScheduledClass.query.filter_by(classroom_id=room1.id).all()
    #     self.assertNotEqual(len(class1s), 0)

    #     for c in class1s:
    #         self.assertLessEqual(len(c.students), 15)

    #     class2s = ScheduledClass.query.filter_by(classroom_id=room2.id).all()
    #     self.assertNotEqual(len(class2s), 0)
        
    #     for c in class2s:
    #         self.assertLessEqual(len(c.students), 10)

    # Duplicated to test student group requirement
    # def test_max_students_in_classroom2(self):
    #     """ It does not assign more students to the course than the maximum for the classroom """
        
    #     self.gen_teachers(5)
    #     stud_list = self.gen_students(20)

    #     room1 = self.gen_classrooms(1, max_student_count=15)[0]
    #     room2 = self.gen_classrooms(1, max_student_count=10)[0]
    #     course = self.gen_courses(1)[0]

    #     db.session.add(ClassroomsCourse(course_id=course.id, classroom_id=room1.id))
    #     db.session.add(ClassroomsCourse(course_id=course.id, classroom_id=room2.id))

    #     sgrp = StudentGroup(name="test student group")
    #     db.session.add(sgrp)
    #     db.session.flush()

    #     for stud in stud_list:
    #         db.session.add(StudentsStudentGroup(student_id=stud.id, student_group_id=sgrp.id))

    #     db.session.add(CoursesStudentGroup(student_group_id=sgrp.id, course_id=course.id))
    #     db.session.commit()

    #     # make sure there is only one time slot per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=900, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     class1s = ScheduledClass.query.filter_by(classroom_id=room1.id).all()
    #     self.assertNotEqual(len(class1s), 0)

    #     for c in class1s:
    #         self.assertLessEqual(len(c.students), 15)

    #     class2s = ScheduledClass.query.filter_by(classroom_id=room2.id).all()
    #     self.assertNotEqual(len(class2s), 0)
        
    #     for c in class2s:
    #         self.assertLessEqual(len(c.students), 10)

    # def test_classroom_course_soft_constraint(self):
    #     """ It chooses classrooms from a list of those with soft constraint to the course """
    #     self.gen_teachers(5)
    #     stud_list = self.gen_students(20)

    #     room1 = self.gen_classrooms(1, max_student_count=30)[0]
    #     room2 = self.gen_classrooms(1, max_student_count=30)[0]
    #     # make some other random classes 
    #     self.gen_classrooms(5)
        
    #     course = self.gen_courses(1)[0]

    #     db.session.add(ClassroomsCourse(course_id=course.id, classroom_id=room1.id))
    #     db.session.add(ClassroomsCourse(course_id=course.id, classroom_id=room2.id))

    #     for stud in stud_list:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course.id))
    #     db.session.commit()

    #     # make sure there is only one time slot per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=900, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     # make sure the rooms used for the course are the ones that are linked to it
    #     classes = ScheduledClass.query.filter_by(course_id=course.id).all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         self.assertIn(c.classroom_id, [room1.id, room2.id])

    # def test_classroom_course_hard_constraint(self):
    #     """ It chooses only the classroom with the hard constraint to assign to the course """
    #     pass

    # def test_classroom_course_no_constraint(self):
    #     """ It chooses any classroom for the course """
    #     self.gen_teachers(5)
    #     stud_list = self.gen_students(20)

    #     room1 = self.gen_classrooms(1, max_student_count=30)[0]
    #     room2 = self.gen_classrooms(1, max_student_count=30)[0]
    #     # make some other random classes 
    #     self.gen_classrooms(5)
        
    #     course = self.gen_courses(1)[0]

    #     for stud in stud_list:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course.id))
    #     db.session.commit()

    #     # make sure there is only one time slot per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=900, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     # make sure the rooms used for the course are the ones that are linked to it
    #     classes = ScheduledClass.query.filter_by(course_id=course.id).all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         self.assertIn(c.classroom_id, Classroom.query.all())

    # def test_classroom_end_time_constraint(self):
    #     """ it does not schedule the classroom outside of the assigned time constraint """
    #     self.gen_teachers(2)
    #     stud_list = self.gen_students(15)

    #     room1 = self.gen_classrooms(1, max_student_count=5, avail_end_time=809)[0]
    #     room2 = self.gen_classrooms(1, max_student_count=6)[0]

    #     course1 = self.gen_courses(1)[0]

    #     # assign the rooms to the courses
    #     db.session.add(ClassroomsCourse(classroom_id=room1.id, course_id=course1.id))
    #     db.session.add(ClassroomsCourse(classroom_id=room2.id, course_id=course1.id))

    #     for stud in stud_list:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course1.id))
    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     # make sure the classes assigned to room1 occur in the proper time slot
    #     classes = ScheduledClass.query.filter_by(classroom_id=room1.id).all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         self.assertLessEqual(c.end_time, 809)

    #     # TODO
    #     # now create a failure condition to be sure we just didn't get luck with the timing
    #     # new_stud_list = self.gen_students(2)

    #     # for stud in new_stud_list:
    #     #     db.session.add(CoursesStudent(student_id=stud.id, course_id=course1.id))
    #     # db.session.commit()

    #     # with timeout(seconds=10):
    #     #     scheduler.make_schedule()
    #     # with self.assertRaises(SchedulerNoSolution): 
    #     # scheduler.make_schedule()

    # def test_classroom_start_time_constraint(self):
    #     """ it does not schedule the classroom outside of the assigned time constraint """
    #     self.gen_teachers(2)
    #     stud_list = self.gen_students(15)

    #     room1 = self.gen_classrooms(1, max_student_count=5, avail_start_time=900)[0]
    #     room2 = self.gen_classrooms(1, max_student_count=6)[0]

    #     course1 = self.gen_courses(1)[0]

    #     # assign the rooms to the courses
    #     db.session.add(ClassroomsCourse(classroom_id=room1.id, course_id=course1.id))
    #     db.session.add(ClassroomsCourse(classroom_id=room2.id, course_id=course1.id))

    #     for stud in stud_list:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course1.id))
    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     # make sure the classes assigned to room1 occur in the proper time slot
    #     classes = ScheduledClass.query.filter_by(classroom_id=room1.id).all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         self.assertGreaterEqual(c.start_time, 900)

    #     # TODO
    #     # now create a failure condition to be sure we just didn't get luck with the timing
    #     # new_stud_list = self.gen_students(2)

    #     # for stud in new_stud_list:
    #     #     db.session.add(CoursesStudent(student_id=stud.id, course_id=course1.id))
    #     # db.session.commit()
    
    # def test_course_start_time_constraint(self):
    #     self.gen_teachers(3)
    #     self.gen_classrooms(2)
    #     stud_list1 = self.gen_students(5)
    #     stud_list2 = self.gen_students(12)

    #     course1 = self.gen_courses(1, max_student_count=5, avail_start_time=800)[0]
    #     course2 = self.gen_courses(1, max_student_count=6)[0]

    #     for stud in stud_list1:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course1.id))
    #     for stud in stud_list2:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course2.id))

    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     classes = ScheduledClass.query.filter_by(course_id=course1.id).all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         self.assertGreaterEqual(c.start_time, 800)

    # def test_course_end_time_constraint(self):
    #     self.gen_teachers(3)
    #     self.gen_classrooms(2)
    #     stud_list1 = self.gen_students(5)
    #     stud_list2 = self.gen_students(12)

    #     course1 = self.gen_courses(1, max_student_count=5, avail_end_time=809)[0]
    #     course2 = self.gen_courses(1, max_student_count=6)[0]

    #     for stud in stud_list1:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course1.id))
    #     for stud in stud_list2:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course2.id))

    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     classes = ScheduledClass.query.filter_by(course_id=course1.id).all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         self.assertLessEqual(c.end_time, 809)

    # def test_teacher_start_time_constraint(self):
    #     self.gen_classrooms(2)
    #     stud_list = self.gen_students(15)

    #     teach1 = self.gen_teachers(1, avail_start_time=900)[0]
    #     teach2 = self.gen_teachers(1)[0]

    #     course = self.gen_courses(1, max_student_count=5)[0]

    #     # assign the teachers to the courses
    #     db.session.add(CoursesTeacher(teacher_id=teach1.id, course_id=course.id))
    #     db.session.add(CoursesTeacher(teacher_id=teach2.id, course_id=course.id))

    #     for stud in stud_list:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course.id))
    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     # make sure the classes assigned to room1 occur in the proper time slot
    #     classes = ScheduledClass.query.filter_by(teacher_id=teach1.id).all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         self.assertGreaterEqual(c.start_time, 900) 

    # def test_teacher_end_time_constraint(self):
    #     self.gen_classrooms(2)
    #     stud_list = self.gen_students(15)

    #     teach1 = self.gen_teachers(1, avail_end_time=809)[0]
    #     teach2 = self.gen_teachers(1)[0]

    #     course = self.gen_courses(1, max_student_count=5)[0]

    #     # assign the teachers to the courses
    #     db.session.add(CoursesTeacher(teacher_id=teach1.id, course_id=course.id))
    #     db.session.add(CoursesTeacher(teacher_id=teach2.id, course_id=course.id))

    #     for stud in stud_list:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course.id))
    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     # make sure the classes assigned to room1 occur in the proper time slot
    #     classes = ScheduledClass.query.filter_by(teacher_id=teach1.id).all()
    #     self.assertNotEqual(len(classes), 0)
    #     for c in classes:
    #         self.assertLessEqual(c.end_time, 809) 

    # def test_classroom_time_no_constraint(self):
    #     """ It is free to assign any time to a classroom """
    #     pass

    # def test_course_student_hard_constraint(self):
    #     """ 
    #     It requires a student to be assigned the course 
    #     """
    #     self.gen_teachers(2)
    #     self.gen_classrooms(2)
    #     stud_list = self.gen_students(10)
    #     course1 = self.gen_courses(1, max_student_count=5)[0]

    #     for stud in stud_list:
    #         db.session.add(CoursesStudent(student_id=stud.id, course_id=course1.id))
    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     all_students = []
    #     for c in ScheduledClass.query.filter_by(course_id=course1.id).all():
    #         all_students += c.students

    #     for s in stud_list:
    #         self.assertIn(s, all_students)

    # def test_subject_student_constraint(self):
    #     """
    #     It requires a student to be assigned to a course within the subject
    #     """
    #     self.gen_teachers(2)
    #     self.gen_classrooms(2)
    #     stud_list = self.gen_students(10)
    #     courses = self.gen_courses(5, max_student_count=5)

    #     subject = self.gen_subjects(1)[0]
    #     for c in courses:
    #         db.session.add(CoursesSubject(course_id=c.id, subject_id=subject.id))
    #     db.session.commit()

    #     for stud in stud_list:
    #         db.session.add(StudentsSubject(student_id=stud.id, subject_id=subject.id))
    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     all_students = []
    #     for course in courses:
    #         for c in ScheduledClass.query.filter_by(course_id=course.id).all():
    #             all_students += c.students

    #     for s in stud_list:
    #         self.assertIn(s, all_students)


    # def test_subject_student_group_constraint(self):
    #     """
    #     It requires a student to be assigned to a course within the subject
    #     """
    #     self.gen_teachers(2)
    #     self.gen_classrooms(2)
    #     stud_list = self.gen_students(10)
    #     sgrp = self.gen_student_groups(1)[0]

    #     for stud in stud_list:
    #         db.session.add(StudentsStudentGroup(student_id=stud.id, student_group_id=sgrp.id))

    #     courses = self.gen_courses(5, max_student_count=5)

    #     subject = self.gen_subjects(1)[0]
    #     for c in courses:
    #         db.session.add(CoursesSubject(course_id=c.id, subject_id=subject.id))
    #     db.session.commit()

    #     db.session.add(StudentGroupsSubject(student_group_id=sgrp.id, subject_id=subject.id))
    #     db.session.commit()

    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     all_students = []
    #     for course in courses:
    #         for c in ScheduledClass.query.filter_by(course_id=course.id).all():
    #             all_students += c.students

    #     for s in sgrp.students:
    #         self.assertIn(s, all_students)

    # def test_course_student_med_constraint(self):
    #     """ It sets a preferred course for a student """
    #     pass

    # def test_course_student_soft_constraint(self):
    #     """ It sets the course as available to the student """
    #     pass

    # def test_course_teacher_hard_constraint(self):
    #     """ It requires the course for the teacher """
    #     self.gen_students(10)
    #     self.gen_teachers(5)
    #     self.gen_courses(5)
    #     self.gen_classrooms(10)

    #     stud_list = self.gen_students(10)
    #     teach = self.gen_teachers(1)[0]
    #     course = self.gen_courses(1)[0]

    #     for s in stud_list:
    #         db.session.add(CoursesStudent(student_id=s.id, course_id=course.id))

    #     db.session.add(CoursesTeacher(course_id=course.id, teacher_id=teach.id))
    #     db.session.commit()
    
    #     # make sure there is only two time slots per day
    #     scheduler = Scheduler(day_start_time=800, break_length=1, 
    #                           day_end_time=909, class_duration=9,
    #                           lunch_start=809, lunch_end=900, class_count=10)
    #     scheduler.make_schedule()

    #     classes = ScheduledClass.query.filter_by(course_id=course.id).all()
    #     self.assertNotEqual(len(classes), 0)
        
    #     for c in classes:
    #         self.assertEqual(c.teacher_id, teach.id)

    # def test_course_teacher_soft_constraint(self):
    #     """ It allows the course to be assigned to the teacher """
    #     pass

    # def test_course_teacher_no_constraint(self):
    #     """ It is free to choose any course for the teacher """
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

    # def test_student_group_time(self):
    #     """ It doesn't schedule the student in the group for classes outside of the start and end time """
    #     pass


    

