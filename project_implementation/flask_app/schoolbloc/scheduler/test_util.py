from schoolbloc import app, db
from schoolbloc.users.models import User, Role
from schoolbloc.scheduler.models import *
from random import *

class SchedulerTestUtilities():
    @staticmethod
    def generate_students(n):
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

    @staticmethod
    def generate_teachers(n, avail_start_time=None, avail_end_time=None):
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

    @staticmethod
    def generate_classrooms(n, max_student_count=None, avail_start_time=None, avail_end_time=None):
        rooms = [ Classroom(room_number=randint(0, 1000000), 
                            max_student_count=max_student_count,
                            avail_start_time=avail_start_time,
                            avail_end_time=avail_end_time) 
                  for i in range(n) ]

        for r in rooms:
            db.session.add(r)
        db.session.commit()
        return rooms

    @staticmethod
    def generate_courses(n, max_student_count=None, avail_start_time=None, avail_end_time=None):
        courses = [ Course(name="course {}".format(randint(0, 1000000)),
                           max_student_count=max_student_count,
                           avail_start_time=avail_start_time,
                           avail_end_time=avail_end_time) 
                    for i in range(n) ]

        for r in courses:
            db.session.add(r)
        db.session.commit()
        return courses

    @staticmethod
    def generate_subjects(n, max_student_count=None):
        subjects = [ Subject(name="subject {}".format(randint(0, 1000000))) for i in range(n) ]

        for r in subjects:
            db.session.add(r)
        db.session.commit()
        return subjects

    @staticmethod
    def generate_student_groups(n):
        student_groups = [ StudentGroup(name="student group {}".format(randint(0, 1000000))) for i in range(n) ]

        for r in student_groups:
            db.session.add(r)
        db.session.commit()
        return student_groups