import unittest
import tempfile
import os
from schoolbloc import app, db
from schoolbloc.users.models import User, Role
from schoolbloc.scheduler.models import *
from schoolbloc.scheduler.scheduler import Scheduler
from schoolbloc.scheduler.test_util import SchedulerTestUtilities as TestUtil


class FullScheduleTests(unittest.TestCase):
    """ Tests full scheduling scenarios """

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        # flaskr.init_db()

        db.session.add(Role(role_type='admin'))
        db.session.add(Role(role_type='teacher'))
        db.session.add(Role(role_type='student'))
        db.session.add(User(username='admin', password='admin', role_type='admin'))
        db.session.add(User(username='teacher', password='teacher', role_type='teacher'))
        db.session.add(User(username='student', password='student', role_type='student'))
        db.session.add(User(username='student2', password='student2', role_type='student'))
        db.session.add(User(username='student3', password='student3', role_type='student'))
        db.session.commit()


    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    # def setUp(self):
    #     """ Uses an in memory sqlite database for testing """

    #     # Clean the DB
    #     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    #     db.init_app(app)
    #     # with app.app_context():
    #     db.drop_all()        
    #     db.create_all()

    #     db.session.add(Role(role_type='admin'))
    #     db.session.add(Role(role_type='teacher'))
    #     db.session.add(Role(role_type='student'))
    #     db.session.commit()

    # def gen_students(self, n):
    #     """ returns n students in a list after saving them to the DB """
    #     s_user_list = [ User('s_user_%s' % random(), 'password', 'teacher') 
    #                     for i in range(n)]
    #     for u in s_user_list: db.session.add(u)
    #     db.session.flush()

    #     stud_list = [ Student(first_name="student_f_%s" % i, 
    #                           last_name="student_l_%s" % i, 
    #                           user_id=s_user_list[i].id) 
    #                   for i in range(n) ]

    #     for s in stud_list: db.session.add(s)
    #     db.session.commit()
    #     return stud_list
        
    def test_vg_fall_2015_a_day(self):
        """ Full test of vanguards schedule A day data for fall semester of 2015 """

        timeblocks = TestUtil.generate_timeblocks(day_start_time=905,
                                                  day_end_time=1325,
                                                  break_length=10,
                                                  lunch_start=1105,
                                                  lunch_end=1205,
                                                  class_duration=50)

        # get a list of sample names
        names = TestUtil.get_names(320)
        
        stud_7th_list = TestUtil.generate_students(100, names=names[0:100])
        stud_8th_list = TestUtil.generate_students(100, names=names[100:200])
        stud_9th_list = TestUtil.generate_students(100, names=names[200:300])

        # Add the teachers
        # teacher_name_list = [("S", "Owen"),("M", "Evans"), ("S", "Evans"), ("J", "Green"),
        #                 ("T", "Gustafson"), ("J", "Hoover"), ("Je", "Jenkins"), ("Jo", "Jenkins"),
        #                 ("K", "Johnson"), ("J", "Kingston"), ("M", "Kingston"), ("R", "Kingston"),
        #                 ("D", "Marvin"), ("M", "Mong"), ("A", "OBrien"), 
        #                 ("V", "Obrien"), ("M. Omer"), ("J", "Palmer"), ("V", "Stowell"), 
        #                 ("D", "Thomas")]

        # teach_list = TestUtil.generate_teachers(20, names[300:320])
        music_teacher_1 = TestUtil.generate_teachers(1, names[300:301])[0]
        music_teacher_2 = TestUtil.generate_teachers(1, names[301:302])[0]
        math_teacher_1 = TestUtil.generate_teachers(1, names[302:303])[0]
        math_teacher_2 = TestUtil.generate_teachers(1, names[303:304])[0]
        math_teacher_3 = TestUtil.generate_teachers(1, names[304:305])[0]
        math_teacher_4 = TestUtil.generate_teachers(1, names[305:306])[0]
        sci_teacher_1 = TestUtil.generate_teachers(1, names[306:307])[0]
        lang_teacher_1 = TestUtil.generate_teachers(1, names[307:308])[0]
        lang_teacher_2 = TestUtil.generate_teachers(1, names[308:309])[0]
        pe_teacher_1 = TestUtil.generate_teachers(1, names[309:310])[0]
        soc_teacher_1 = TestUtil.generate_teachers(1, names[310:311])[0]
        soc_teacher_2 = TestUtil.generate_teachers(1, names[311:312])[0]
        tech_teacher_1 = TestUtil.generate_teachers(1, names[312:313])[0]
        learn_teacher_1 = TestUtil.generate_teachers(1, names[313:314])[0]
        pe_teacher_2 = TestUtil.generate_teachers(1, names[314:315])[0]
        pe_teacher_3 = TestUtil.generate_teachers(1, names[315:316])[0]
        extra_teachers = TestUtil.generate_teachers(4, names[316:320])

        # Add the rooms
        room_numbers = [203, 215, 220, 216, 109, 207, 201, 205, 210, 214, 
                        213, 219, 217, 218, 107, 209, 208, 206]
        classroom_list = [ Classroom(room_number=r) for r in room_numbers ]
        for r in classroom_list: db.session.add(r)
        db.session.flush()
        
        # attach some teachers to some rooms
        db.session.add(ClassroomsTeacher(teacher_id=music_teacher_1.id, classroom_id=classroom_list[0].id))
        db.session.add(ClassroomsTeacher(teacher_id=math_teacher_1.id, classroom_id=classroom_list[2].id))
        db.session.add(ClassroomsTeacher(teacher_id=math_teacher_4.id, classroom_id=classroom_list[5].id))
        db.session.add(ClassroomsTeacher(teacher_id=sci_teacher_1.id, classroom_id=classroom_list[6].id))
        db.session.add(ClassroomsTeacher(teacher_id=soc_teacher_1.id, classroom_id=classroom_list[10].id))
        db.session.add(ClassroomsTeacher(teacher_id=tech_teacher_1.id, classroom_id=classroom_list[12].id))
        db.session.add(ClassroomsTeacher(teacher_id=extra_teachers[0].id, classroom_id=classroom_list[15].id))
        db.session.add(ClassroomsTeacher(teacher_id=extra_teachers[1].id, classroom_id=classroom_list[16].id))

        # Add courses and subjects
        sub_music = Subject(name="Music")
        db.session.add(sub_music)
        cl_music = [ Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=30) 
                      for c_name in ["Beg Band", "Int Band",  "Beg Orch", "Int Orchestra",
                                     "Girls Choir", "Boys Choir",
                                     "Musical Theatre", "Concert Choir", "Madrigals"] ]
        for c in cl_music: db.session.add(c)
        db.session.flush()

        # add a teacher for this subject
        db.session.add(TeachersSubject(teacher_id=music_teacher_1.id, subject_id=sub_music.id))
        db.session.add(TeachersSubject(teacher_id=music_teacher_2.id, subject_id=sub_music.id))

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_music.id) for c in cl_music ]
        for cs in csubs: db.session.add(cs)

        sub_7th_math = Subject(name="7th Math")
        db.session.add(sub_7th_math)
        cl_7th_math = [Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=30) 
                       for c_name in ["7th Grade Math", "Secondary Math I", "Secondary Math II"] ]
        for c in cl_7th_math: db.session.add(c)
        db.session.flush()

        # add a teacher for this subject
        db.session.add(TeachersSubject(teacher_id=math_teacher_1.id, subject_id=sub_7th_math.id))
        db.session.add(TeachersSubject(teacher_id=math_teacher_2.id, subject_id=sub_7th_math.id))

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_7th_math.id) for c in cl_7th_math ]
        for cs in csubs: db.session.add(cs)

        sub_8th_math = Subject(name="8th Math")
        db.session.add(sub_8th_math)
        cl_8th_math = [Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=30)
                        for c_name in ["8th Grade Math",  
                                       "Secondary Math I", "Secondary Math II", "Secondary Math III"] ]
        for c in cl_8th_math: db.session.add(c)
        db.session.flush()

        # add a teacher for this subject
        db.session.add(TeachersSubject(teacher_id=math_teacher_2.id, subject_id=sub_8th_math.id))
        db.session.add(TeachersSubject(teacher_id=math_teacher_3.id, subject_id=sub_8th_math.id))
        db.session.add(TeachersSubject(teacher_id=math_teacher_4.id, subject_id=sub_8th_math.id))

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_8th_math.id) for c in cl_8th_math ]
        for cs in csubs: db.session.add(cs)

        sub_9th_math = Subject(name="9th Math")                               
        db.session.add(sub_9th_math)
        cl_9th_math = [ Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=30)  
                        for c_name in ["9th Grade Math", "Secondary Math I", "Secondary Math II", "Secondary Math III"] ]
        
        for c in cl_9th_math: db.session.add(c)
        db.session.flush()

        # add a teacher for this subject
        db.session.add(TeachersSubject(teacher_id=math_teacher_1.id, subject_id=sub_9th_math.id))
        db.session.add(TeachersSubject(teacher_id=math_teacher_2.id, subject_id=sub_9th_math.id))

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_9th_math.id) for c in cl_9th_math ]
        for cs in csubs: db.session.add(cs)

        course_7th_sci = Course(name="Int Science (7)", duration=82, 
                            min_student_count=0,
                            max_student_count=25)
        db.session.add(course_7th_sci)
        db.session.flush()

        # add a teacher for this course
        db.session.add(CoursesTeacher(teacher_id=math_teacher_4.id, course_id=course_7th_sci.id))

        course_8th_sci = Course(name="Int Science (8)", duration=82, 
                            min_student_count=0,
                            max_student_count=25)
        db.session.add(course_8th_sci)
        db.session.flush()

        # add a teacher for this course
        db.session.add(CoursesTeacher(teacher_id=sci_teacher_1.id, course_id=course_7th_sci.id))

        course_9th_sci = Course(name="Int Science (9)", duration=82, 
                            min_student_count=0,
                            max_student_count=25)
        db.session.add(course_9th_sci)

        course_7th_la = Course(name="Language Arts (7)", duration=82, 
                            min_student_count=0,
                            max_student_count=25)
        db.session.add(course_7th_la)

        course_8th_la = Course(name="Language Arts (8)", duration=82, 
                            min_student_count=0,
                            max_student_count=25)
        db.session.add(course_8th_la)
        db.session.flush()

        # add a teacher for this course
        db.session.add(CoursesTeacher(teacher_id=lang_teacher_1.id, course_id=course_8th_la.id))
        db.session.add(CoursesTeacher(teacher_id=lang_teacher_2.id, course_id=course_8th_la.id))

        course_9th_la = Course(name="Language Arts (9)", duration=82, 
                            min_student_count=0,
                            max_student_count=35)
        db.session.add(course_9th_la)
        db.session.flush()

        # add a teacher for this course
        db.session.add(CoursesTeacher(teacher_id=lang_teacher_1.id, course_id=course_9th_la.id))
        db.session.add(CoursesTeacher(teacher_id=lang_teacher_2.id, course_id=course_9th_la.id))

        course_7th_pe = Course(name="PE/Health (7)", duration=82, 
                            min_student_count=0,
                            max_student_count=50)
        db.session.add(course_7th_pe)
        db.session.flush()

        # add a teacher for this course
        db.session.add(CoursesTeacher(teacher_id=pe_teacher_1.id, course_id=course_7th_pe.id))

        course_8th_pe = Course(name="PE/Health (8)", duration=82, 
                            min_student_count=0,
                            max_student_count=50)
        db.session.add(course_8th_pe)
        db.session.flush()

        # add a teacher for this course
        db.session.add(CoursesTeacher(teacher_id=pe_teacher_2.id, course_id=course_8th_pe.id))
        db.session.add(CoursesTeacher(teacher_id=pe_teacher_3.id, course_id=course_8th_pe.id))

        course_9th_pe = Course(name="PE/Health (9)", duration=82, 
                            min_student_count=0,
                            max_student_count=50)
        db.session.add(course_9th_pe)
        db.session.flush()

        # add a teacher for this course
        db.session.add(CoursesTeacher(teacher_id=pe_teacher_2.id, course_id=course_9th_pe.id))
        db.session.add(CoursesTeacher(teacher_id=pe_teacher_3.id, course_id=course_9th_pe.id))

        course_leadership = Course(name="Leadership", duration=82, 
                            min_student_count=0,
                            max_student_count=25)
        db.session.add(course_leadership)

        sub_soc_stud = Subject(name="Social Studies")                               
        db.session.add(sub_soc_stud)
        cl_soc_stud = [ Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=30)  
                        for c_name in ["Student Govt", "Utah Studies", "US History I", "World Geog"] ]
        for c in cl_soc_stud: db.session.add(c)
        db.session.flush()

        # add a teacher for this course
        db.session.add(TeachersSubject(teacher_id=soc_teacher_1.id, subject_id=sub_soc_stud.id))
        db.session.add(TeachersSubject(teacher_id=soc_teacher_2.id, subject_id=sub_soc_stud.id))

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_soc_stud.id) for c in cl_soc_stud ]
        for cs in csubs: db.session.add(cs)

        sub_tech = Subject(name="Technology")                               
        db.session.add(sub_tech)
        cl_tech = [ Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=15)  
                        for c_name in ["Technology", "Computer Essentials", "Robotics" "Computer Tech", "Pre Engineering", "Auto"] ]
        for c in cl_tech: db.session.add(c)
        db.session.flush()

        db.session.add(TeachersSubject(teacher_id=tech_teacher_1.id, subject_id=sub_tech.id))
     
        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_tech.id) for c in cl_tech ]
        for cs in csubs: db.session.add(cs)

        sub_learning = Subject(name="Learning")                               
        db.session.add(sub_learning)
        cl_learning = [ Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=35)  
                        for c_name in ["Learning Strategies", "College & Career Awareness"] ]
        for c in cl_learning: db.session.add(c)
        db.session.flush()

        db.session.add(TeachersSubject(teacher_id=learn_teacher_1.id, subject_id=sub_learning.id))

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_learning.id) for c in cl_learning ]
        for cs in csubs: db.session.add(cs)

        db.session.flush()

        ### now add the constraints
        
        # # add student groups
        sg_7th_grade = StudentGroup(name="7th Grade")
        sg_8th_grade = StudentGroup(name="8th Grade")
        sg_9th_grade = StudentGroup(name="9th Grade")
        sg_list = [sg_7th_grade, sg_8th_grade] #, sg_8th_grade, sg_9th_grade]

        db.session.add(sg_7th_grade)
        db.session.add(sg_8th_grade)
        db.session.add(sg_9th_grade)
        db.session.flush()

        # # assign students to each group, 100 each
        students_7th_grade = []
        students_8th_grade = []
        students_9th_grade = []
        for stud in stud_7th_list:
            students_7th_grade.append(stud)
            ssg = StudentsStudentGroup(student_group_id=sg_7th_grade.id, student_id=stud.id)
            db.session.add(ssg)

        for stud in stud_8th_list:
            students_8th_grade.append(stud)
            ssg = StudentsStudentGroup(student_group_id=sg_8th_grade.id, student_id=stud.id)
            db.session.add(ssg)

        for stud in stud_9th_list:
            students_9th_grade.append(stud)
            ssg = StudentsStudentGroup(student_group_id=sg_9th_grade.id, student_id=stud.id)
            db.session.add(ssg)

        # add course assignments to each student group
        # NOTE: This set pushes the student booking over the number of time blocks
        # for sg in sg_list: db.session.add(StudentGroupsSubject(subject_id=sub_music.id, student_group_id=sg.id))
        # for sg in sg_list: db.session.add(StudentGroupsSubject(subject_id=sub_soc_stud.id, student_group_id=sg.id))
        # for sg in sg_list: db.session.add(StudentGroupsSubject(subject_id=sub_tech.id, student_group_id=sg.id))
        # for sg in sg_list: db.session.add(StudentGroupsSubject(subject_id=sub_learning.id, student_group_id=sg.id))

        db.session.add(StudentGroupsSubject(subject_id=sub_7th_math.id, 
                                            student_group_id=sg_7th_grade.id, 
                                            priority="low"))
        db.session.add(StudentGroupsSubject(subject_id=sub_8th_math.id, 
                                            student_group_id=sg_8th_grade.id,
                                            priority="low"))
        db.session.add(StudentGroupsSubject(subject_id=sub_9th_math.id, 
                                            student_group_id=sg_9th_grade.id,
                                            priority="low"))

        db.session.add(CoursesStudentGroup(course_id=course_7th_sci.id, 
                                           student_group_id=sg_7th_grade.id,
                                           priority="low"))
        db.session.add(CoursesStudentGroup(course_id=course_8th_sci.id, 
                                           student_group_id=sg_8th_grade.id,
                                           priority="low"))
        db.session.add(CoursesStudentGroup(course_id=course_9th_sci.id, 
                                           student_group_id=sg_9th_grade.id,
                                           priority="low"))

        db.session.add(CoursesStudentGroup(course_id=course_7th_la.id, 
                                           student_group_id=sg_7th_grade.id,
                                           priority="low"))
        db.session.add(CoursesStudentGroup(course_id=course_8th_la.id, 
                                           student_group_id=sg_8th_grade.id,
                                           priority="low"))
        db.session.add(CoursesStudentGroup(course_id=course_9th_la.id, 
                                           student_group_id=sg_9th_grade.id,
                                           priority="low"))

        db.session.add(CoursesStudentGroup(course_id=course_7th_pe.id, 
                                           student_group_id=sg_7th_grade.id,
                                           priority="low"))
        db.session.add(CoursesStudentGroup(course_id=course_8th_pe.id, 
                                           student_group_id=sg_8th_grade.id,
                                           priority="low"))
        db.session.add(CoursesStudentGroup(course_id=course_9th_pe.id, 
                                           student_group_id=sg_9th_grade.id,
                                           priority="low"))

        db.session.add(CoursesStudentGroup(course_id=course_leadership.id, 
                                           student_group_id=sg_7th_grade.id,
                                           priority="low"))
        db.session.add(CoursesStudentGroup(course_id=course_leadership.id, 
                                           student_group_id=sg_8th_grade.id,
                                           priority="low"))
        db.session.add(CoursesStudentGroup(course_id=course_leadership.id, 
                                           student_group_id=sg_9th_grade.id,
                                           priority="low"))

        db.session.commit()

        # make the schedule
        scheduler = Scheduler() 
        
        # self.assertEqual(scheduler.calc_course_count(), {})
        # with timeout(seconds=30):
        scheduler.make_schedule()

        # did we get a student-course maping for the CoursesStudentGroups?
        # s_ids = []
        # for c in ScheduledClass.query.filter_by(course_id=course_7th_sci.id):
        #     stud_list = ScheduledClassesStudent.filter_by(scheduled_class_id=c.id)
        #     s_ids += [ s.id for s in stud_list ]

        # for s in students_7th_grade:
        #     self.assertIn(s.id, s_ids)