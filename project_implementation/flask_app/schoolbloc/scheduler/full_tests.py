import unittest
from schoolbloc import app, db
from schoolbloc.users.models import User, Role
from schoolbloc.scheduler.models import (Teacher, Classroom, ClassroomsCourse, 
                                         Course, CoursesTeacher, CoursesStudent, 
                                         CoursesStudentGroup, CoursesSubject,
                                         Student, StudentsStudentGroup, StudentGroup,
                                         ScheduledClass, ScheduledClassesStudent,
                                         Subject, StudentGroupsSubject)
from schoolbloc.scheduler.scheduler import Scheduler


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
        s_user_list = [ User('s_user_%s' % i, 'password', 'student') for i in range(30)]
        for u in s_user_list: db.session.add(u)
        db.session.flush()

        stud_list = [ Student(first_name="first_name_%s" % i, 
                              last_name="last_name_%s" % i, 
                              user_id=s_user_list[i].id) for i in range(30) ]
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

        # Add courses and subjects
        sub_music = Subject(name="Music")
        db.session.add(sub_music)
        cl_music = [ Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=20) 
                      for c_name in ["Beg Band", "Int Band",  "Beg Orch", "Int Orchestra",
                                     "Girls Choir", "Boys Choir",
                                     "Musical Theatre", "Concert Choir", "Madrigals"] ]
        for c in cl_music: db.session.add(c)
        db.session.flush()

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_music.id) for c in cl_music ]
        for cs in csubs: db.session.add(cs)

        sub_7th_math = Subject(name="7th Math")
        db.session.add(sub_7th_math)
        cl_7th_math = [Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=20) 
                       for c_name in ["7th Grade Math", "8th Grade Math",  
                                      "Secondary Math I", "Secondary Math II", "Secondary Math III"] ]
        for c in cl_7th_math: db.session.add(c)
        db.session.flush()

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_7th_math.id) for c in cl_7th_math ]
        for cs in csubs: db.session.add(cs)

        sub_8th_math = Subject(name="8th Math")
        db.session.add(sub_8th_math)
        cl_8th_math = [Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=20)
                        for c_name in ["8th Grade Math",  
                                       "Secondary Math I", "Secondary Math II", "Secondary Math III"] ]
        for c in cl_8th_math: db.session.add(c)
        db.session.flush()

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_8th_math.id) for c in cl_8th_math ]
        for cs in csubs: db.session.add(cs)

        sub_9th_math = Subject(name="9th Math")                               
        db.session.add(sub_9th_math)
        cl_9th_math = [ Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=20)  
                        for c_name in ["9th Grade Math", "Secondary Math I", "Secondary Math II", "Secondary Math III"] ]
        
        for c in cl_9th_math: db.session.add(c)
        db.session.flush()

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_9th_math.id) for c in cl_9th_math ]
        for cs in csubs: db.session.add(cs)

        course_7th_sci = Course(name="Int Science (7)", duration=82, 
                            min_student_count=0,
                            max_student_count=20)
        db.session.add(course_7th_sci)

        course_8th_sci = Course(name="Int Science (8)", duration=82, 
                            min_student_count=0,
                            max_student_count=20)
        db.session.add(course_8th_sci)

        course_9th_sci = Course(name="Int Science (9)", duration=82, 
                            min_student_count=0,
                            max_student_count=20)
        db.session.add(course_9th_sci)

        course_7th_la = Course(name="Language Arts (7)", duration=82, 
                            min_student_count=0,
                            max_student_count=20)
        db.session.add(course_7th_la)

        course_8th_la = Course(name="Language Arts (8)", duration=82, 
                            min_student_count=0,
                            max_student_count=20)
        db.session.add(course_8th_la)

        course_9th_la = Course(name="Language Arts (9)", duration=82, 
                            min_student_count=0,
                            max_student_count=20)
        db.session.add(course_9th_la)

        course_7th_pe = Course(name="PE/Health (7)", duration=82, 
                            min_student_count=0,
                            max_student_count=20)
        db.session.add(course_7th_pe)

        course_8th_pe = Course(name="PE/Health (8)", duration=82, 
                            min_student_count=0,
                            max_student_count=20)
        db.session.add(course_8th_pe)

        course_9th_pe = Course(name="PE/Health (9)", duration=82, 
                            min_student_count=0,
                            max_student_count=20)
        db.session.add(course_9th_pe)

        course_leadership = Course(name="Leadership", duration=82, 
                            min_student_count=0,
                            max_student_count=20)
        db.session.add(course_leadership)

        sub_soc_stud = Subject(name="Social Studies")                               
        db.session.add(sub_soc_stud)
        cl_soc_stud = [ Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=20)  
                        for c_name in ["Student Govt", "Utah Studies", "US History I", "World Geog"] ]
        for c in cl_soc_stud: db.session.add(c)
        db.session.flush()

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_soc_stud.id) for c in cl_soc_stud ]
        for cs in csubs: db.session.add(cs)

        sub_tech = Subject(name="Technology")                               
        db.session.add(sub_tech)
        cl_tech = [ Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=20)  
                        for c_name in ["Technology", "Computer Essentials", "Robotics" "Computer Tech", "Pre Engineering", "Auto"] ]
        for c in cl_tech: db.session.add(c)
        db.session.flush()

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_tech.id) for c in cl_tech ]
        for cs in csubs: db.session.add(cs)

        sub_learning = Subject(name="Learning")                               
        db.session.add(sub_learning)
        cl_learning = [ Course(name=c_name, duration=82, 
                            min_student_count=0,
                            max_student_count=20)  
                        for c_name in ["Learning Strategies", "College & Career Awareness"] ]
        for c in cl_learning: db.session.add(c)
        db.session.flush()

        csubs = [ CoursesSubject(course_id=c.id, subject_id=sub_learning.id) for c in cl_learning ]
        for cs in csubs: db.session.add(cs)

        db.session.flush()

        ### now add the constraints
        
        # # add student groups
        sg_7th_grade = StudentGroup(name="7th Grade")
        sg_8th_grade = StudentGroup(name="8th Grade")
        # sg_9th_grade = StudentGroup(name="9th Grade")
        sg_list = [sg_7th_grade, sg_8th_grade] #, sg_8th_grade, sg_9th_grade]

        db.session.add(sg_7th_grade)
        db.session.add(sg_8th_grade)
        # db.session.add(sg_9th_grade)
        db.session.flush()

        # # assign students to each group, 100 each
        students_7th_grade = []
        students_8th_grade = []
        # students_9th_grade = []
        for i in range(10):
            stud = stud_list[i]
            students_7th_grade.append(stud)
            ssg = StudentsStudentGroup(student_group_id=sg_7th_grade.id, student_id=stud.id)
            db.session.add(ssg)

        for i in range(10):
            stud = stud_list[i+10]
            students_8th_grade.append(stud)
            ssg = StudentsStudentGroup(student_group_id=sg_8th_grade.id, student_id=stud.id)
            db.session.add(ssg)

        # for i in range(10):
        #     stud = stud_list[i+200]
        #     students_9th_grade.append(stud)
        #     ssg = StudentsStudentGroup(student_group_id=sg_9th_grade.id, student_id=stud.id)
        #     db.session.add(ssg)

        # add course assignments to each student group
        # for sg in sg_list: db.session.add(StudentGroupsSubject(subject_id=sub_music.id, student_group_id=sg.id))
        # for sg in sg_list: db.session.add(StudentGroupsSubject(subject_id=sub_soc_stud.id, student_group_id=sg.id))
        # for sg in sg_list: db.session.add(StudentGroupsSubject(subject_id=sub_tech.id, student_group_id=sg.id))
        # for sg in sg_list: db.session.add(StudentGroupsSubject(subject_id=sub_learning.id, student_group_id=sg.id))

        db.session.add(StudentGroupsSubject(subject_id=sub_7th_math.id, 
                                   student_group_id=sg_7th_grade.id))
        db.session.add(StudentGroupsSubject(subject_id=sub_8th_math.id, 
                             student_group_id=sg_8th_grade.id))
        # db.session.add(StudentGroupsSubject(subject_id=sub_9th_math.id, 
        #                      student_group_id=sg_9th_grade.id))

        db.session.add(CoursesStudentGroup(course_id=course_7th_sci.id, 
                            student_group_id=sg_7th_grade.id))
        db.session.add(CoursesStudentGroup(course_id=course_8th_sci.id, 
                            student_group_id=sg_8th_grade.id))
        # db.session.add(CoursesStudentGroup(course_id=course_9th_sci.id, 
        #                     student_group_id=sg_9th_grade.id))

        db.session.add(CoursesStudentGroup(course_id=course_7th_la.id, 
                            student_group_id=sg_7th_grade.id))
        db.session.add(CoursesStudentGroup(course_id=course_8th_la.id, 
                            student_group_id=sg_8th_grade.id))
        # db.session.add(CoursesStudentGroup(course_id=course_9th_la.id, 
        #                     student_group_id=sg_9th_grade.id))

        db.session.add(CoursesStudentGroup(course_id=course_7th_pe.id, 
                            student_group_id=sg_7th_grade.id))
        db.session.add(CoursesStudentGroup(course_id=course_8th_pe.id, 
                            student_group_id=sg_8th_grade.id))
        # db.session.add(CoursesStudentGroup(course_id=course_9th_pe.id, 
        #                     student_group_id=sg_9th_grade.id))

        db.session.add(CoursesStudentGroup(course_id=course_leadership.id, 
                            student_group_id=sg_7th_grade.id))
        db.session.add(CoursesStudentGroup(course_id=course_leadership.id, 
                            student_group_id=sg_8th_grade.id))
        # db.session.add(CoursesStudentGroup(course_id=course_leadership.id, 
        #                     student_group_id=sg_9th_grade.id))

        db.session.commit()

        # make the schedule
        scheduler = Scheduler(day_start_time=830,
                              day_end_time=1300,
                              break_length=5,
                              lunch_start=1086,
                              lunch_end=1131,
                              class_duration=82) 
        
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