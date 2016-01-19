import unittest
from schoolbloc import app, db
from schoolbloc.users.models import User, Role
from schoolbloc.teachers.models import Teacher
from schoolbloc.classrooms.models import Classroom
from schoolbloc.classrooms.models import ClassroomsCourse
from schoolbloc.courses.models import Course, CoursesTeacher, CoursesStudent, CoursesStudentGroup
from schoolbloc.scheduler.scheduler import Scheduler
from schoolbloc.students.models import Student
from schoolbloc.schedules.models import ScheduledClass, ScheduledClassesStudent, ScheduledClassesStudent

class FullScheduleTests(unittest.TestCase):
    """ Tests full scheduling scenarios """

    def setUp(self):
        """ Uses an in memory sqlite database for testing """

        # Clean the DB
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.init_app(app)
        with app.app_context():
            db.drop_all()        
            db.create_all()

        db.session.add(Role(role_type='admin'))
        db.session.add(Role(role_type='teacher'))
        db.session.add(Role(role_type='student'))
        db.session.commit()
        
    def test_vg_fall_2015_a_day(self):
        """ Full test of vanguards schedule A day data for fall semester of 2015 """

        # Add the students
        s_user_list = [ User('s_user_%s' % i, 'password', 'student') for i in range(300)]
        for u in s_user_list: db.session.add(u)
        db.session.flush()

        stud_list = [ Student(first_name="first_name_%s" % i, 
                              last_name="last_name_%s" % i, 
                              user_id=s_user_list[i].id) for i in range(300) ]
        for s in stud_list: db.session.add(s)

        # Add the teachers
        teacher_list = [("S", "Owen"),("M", "Evans"), ("S", "Evans"), ("J", "Green"),
                        ("T", "Gustafson"), ("J", "Hoover"), ("Je", "Jenkins"), ("Jo", "Jenkins"),
                        ("K", "Johnson"), ("J", "Kingston"), ("M", "Kingston"), ("R", "Kingston"),
                        ("D", "Marvin"), ("M", "Mong"), ("A", "OBrien"), 
                        ("V", "Obrien"), ("M. Omer"), ("J", "Palmer"), ("V", "Stowell"), 
                        ("D", "Thomas")]

        t_user_list = [ User("{}_{}".format(t[0], t[1]), t[0], 'teacher') for t in teacher_list ]
        for t in t_user_list: db.session.add(t)
        db.session.flush()

        t_model_list = [ Teacher(first_name=teacher_list[i][0], 
                                 last_name=teacher_list[i][1], 
                                 user_id=t_user_list[i].id) for i in range(len(teacher_list)) ]
        for t in t_model_list: db.session.add(t)

        # Add the rooms
        room_list = [203, 215, 220, 216, 109, 207, 201, 205, 210, 214, 
                     213, 219, 217, 218, 107, 209, 208, 206]
        r_model_list = [ Classroom(room_number=r) for r in room_list ]
        for r in r_model_list: db.session.add(r)

        # Add the courses
        course_list = ["7th Grade Math", "8th Grade Math", "Math Lab", 
                       "Secondary Math I", "Secondary Math II", "Secondary Math III", 
                       "Int Science (7)", "Int Science (8)", 
                       "Beg Band", "Int Band",  "Beg Orch", "Int Orchestra",
                       "Girls Choir", "Boys Choir",
                       "Musical Theatre", "Concert Choir", "Madrigals"
                       "7th PE/Health", "8th PE/Health", "9th PE/Health", 
                       "Leadership", "Learning Strategies", "College & Career Awareness",
                       "FACS", "Pre Engineering", "Student Govt", "Utah Studies 7",
                       "US History I", "Comp Tech",  "Int Science (8)", 
                       "World Geog (9)", "Auto", "Chemistry (9)",  
                       "Language Arts 7", "Language Arts 8", "Language Arts 10",
                       "Technology", "Computer Essentials", "Robotics" "Computer Tech"]
        c_model_list = [ Course(name=c, duration=82, 
                                min_student_count=0, 
                                max_student_count=60) for c in course_list ]

        for c in c_model_list: db.session.add(c)

        db.session.flush()

        # now add the constraints
        # TODO

        db.session.commit()

        # make the schedule
        scheduler = Scheduler(day_start_time=830,
                              day_end_time=1300,
                              break_length=5,
                              lunch_start=1086,
                              lunch_end=1131,
                              class_duration=82,
                              class_count=60) # normally 70
        scheduler.make_schedule()

