from z3 import *
from schoolbloc.scheduler.models import *
from schoolbloc import db
from schoolbloc.config import config
from functools import wraps
# import errno
# import os
# import signal
import time

DEFAULT_MAX_CLASS_SIZE = 29

# make the class z3 data type and define its constructor
# a class represents a mapping of teacher, room, course, time, and students
# Z3 will choose integers for teacher, room, course, and time. Its our job to
# restrict the choices of integer to only valid IDs of correspoding DB objects
SchClass = Datatype('SchClass')

# we also need to make a TimeBlock Class because the start and end time properties matter
# when determining the schedule
TimeBlock = Datatype('TimeBlock')
TimeBlock.declare('start_end', ('start', IntSort()), ('end', IntSort()))

# with the TimeBlock we can now declare the structure of SchClass
SchClass.declare('SchClass', ('teacher', IntSort()),
                             ('room', IntSort()),
                             ('time', TimeBlock),
                             ('course', IntSort()),
                             ('students', ArraySort(IntSort(), IntSort())))

TimeBlock, SchClass = CreateDatatypes(TimeBlock, SchClass)



class SchedulerNoSolution(Exception):
    pass

class Scheduler():

    def __init__(self, day_start_time=None, 
                       day_end_time=None, 
                       break_length=None, 
                       lunch_start=None, 
                       lunch_end=None,
                       class_duration=None,
                       class_count=None):
        
        self.class_count = class_count or 15
        # if values aren't provided, get the defaults from the config file
        self.day_start_time = day_start_time or config.school_start_time
        self.day_end_time = day_end_time or config.school_end_time
        self.break_length = break_length or config.time_between_classes
        self.lunch_start = lunch_start or config.lunch_start
        self.lunch_end = lunch_end or config.lunch_end
        self.class_duration = class_duration or config.block_size
        self.errors = [] # container to hold error messages

        # Right now, we make more classes than we need so that Z3 can be free to choose
        # the right class for each constraint. later, we'll remove the unused class objects
        self.classes = [Const("class_%s" % (i + 1), SchClass) for i in range(self.class_count)]
    
        self.cur_name_int = 0

    def __repr__(self):
        return "<day_start_time={} day_end_time={} break_length={} lunch_start={} lunch_end={} class_duration={}>".format(
            self.day_start_time, self.day_end_time, self.break_length, self.lunch_start, self.lunch_end, self.class_duration)

    # integer scope in z3 isn't the same as in python, we have to give each 
    # integer a unique name in the constructor to prevent collisions in the solver.
    # we'll use a helper method to make this easier
    def next_int_name(self):
        self.cur_name_int += 1
        return "x%s" % self.cur_name_int

    # We setup some shortcuts to the accessors in the class constructor above just to make
    # coding easier and more readable
    def teacher(self, i):
        return SchClass.teacher(self.classes[i])

    def room(self, i):
        return SchClass.room(self.classes[i])

    def course(self, i):
        return SchClass.course(self.classes[i])

    def time(self, i):
        return SchClass.time(self.classes[i])

    def students(self, i):
        return SchClass.students(self.classes[i])

    # Some sanity checking
    def check_teacher_reqs():
        pass
        # """
        # Makes sure there is a teacher that can teach each course
        # """

        # """
        # Makes sure there are enough teachers that can teach each course. 
        # """

    def check_student_reqs(self):
        """
        Makes sure each student isn't assigned to more classes than they can take
        in a single schedule.
        """
        # determine the number of classes per day
        num_classes = self.number_of_classes()

        for student in Student.query.all():
            count = 0
            count += StudentsSubject.query.filter_by(student_id=student.id).count()
            count += CoursesStudent.query.filter_by(student_id=student.id).count()
            # add the courses for the student groups this student is part of
            for sgrp in StudentsStudentGroup.query.filter_by(student_id=student.id):
                count += StudentGroupsSubject.query.filter_by(student_group_id=sgrp.id).count()
                count += CoursesStudentGroup.query.filter_by(student_group_id=sgrp.id).count()

            if count > num_classes:
                self.errors.append("Student {} is assigned to {} classes and there are only {} class blocks available".format(
                                    student.id, count, num_classes))

    def number_of_classes(self):
        """ 
        Calculates the number of classes per schedule
        """
        count = 0        
        cur_time = self.day_start_time
        while cur_time < self.lunch_start:
            count += 1
            cur_time += self.class_duration + self.break_length

        cur_time = self.lunch_end
        while cur_time < self.day_end_time:
            count += 1
            cur_time += self.class_duration + self.break_length         

        return count

    def max_class_size(self, course_id=None, classroom_id=None):
        """ 
        Determines the maximum student count based on the given course and/or classroom.
        The max count is the lesser of the two if both course and classroom are given.
        """
        
        class_size = DEFAULT_MAX_CLASS_SIZE

        if course_id: 
            course = Course.query.get(course_id)
        else:
            course = None

        if classroom_id:
            classroom = Classroom.query.get(classroom_id)
        else:
            classroom = None

        if course and course.max_student_count:
            if classroom and classroom.max_student_count:
                class_size = min(course.max_student_count, classroom.max_student_count)
            else:
                class_size = course.max_student_count
        else:
            if classroom and classroom.max_student_count:
                class_size = classroom.max_student_count

        return class_size

    # ensures the teacher, room, and course ids are valid. We also allow an id
    # of 0 which means null was chosen by the scheduler
    def ensure_valid_ids(self):

        teacher_ids = [t.id for t in Teacher.query.all()]
        teacher_ids.append(0)
        room_ids = [r.id for r in Classroom.query.all()]
        room_ids.append(0)
        course_ids = [c.id for c in Course.query.all()]
        course_ids.append(0)
        student_ids = [s.id for s in Student.query.all()]
        student_ids.append(0)

        # this basically loops through each class, and then each of the lists above and makes
        # an 'assert equal' for each. The lists are put in an 'Or' constraint to ensure
        # each entry appears in the respective id list
        cons_list = [ And(Or([self.teacher(i) == t_id for t_id in teacher_ids]),
                          Or([self.room(i) == r_id for r_id in room_ids]),
                          Or([self.course(i) == c_id for c_id in course_ids]))
                      for i in range(self.class_count)]

        # make sure valid student IDs are selected. 
        x = Int(self.next_int_name())
        cons_list += [ ForAll(x, Or([self.students(i)[x] == j for j in student_ids]))
                        for i in range(self.class_count) ]

        return cons_list

    def ensure_valid_times(self):

        return [ If(And(self.course(i) != 0, self.room(i) != 0, self.teacher(i) != 0),
                    And(TimeBlock.start(self.time(i)) >= 0,
                        TimeBlock.end(self.time(i)) > TimeBlock.start(self.time(i)),
                        TimeBlock.end(self.time(i)) <= 2359),
                    True)
                 for i in range(self.class_count) ]

    def ensure_valid_class_durations(self):
        """ returns a list of z3 constraints to make sure each class is either its
            specified duration or the default duration. 
            Ignores courses with id == 0 """
        cons_list = []
        for c in Course.query.all():
            if c.duration:
                cons_list += [ If(And(self.course(i) == c.id, self.teacher(i) != 0, self.room(i) != 0),
                                  TimeBlock.end(self.time(i)) - TimeBlock.start(self.time(i)) == c.duration,
                                  True) for i in range(self.class_count) ]
            else:
                cons_list += [ If(And(self.course(i) == c.id, self.teacher(i) != 0, self.room(i) != 0),
                                  TimeBlock.end(self.time(i)) - TimeBlock.start(self.time(i)) == self.class_duration,
                                  True) for i in range(self.class_count) ] 
        return cons_list

    def ensure_valid_class_start_times(self):
        """ returns a list of z3 constraints to make sure each class falls into a 
            valid start time. """
        # calculate the valid start times based on the config vars
        start_times = []
        cur_time = self.day_start_time
        while cur_time < self.lunch_start:
            start_times.append(cur_time)
            cur_time += self.class_duration + self.break_length

        cur_time = self.lunch_end
        while cur_time < self.day_end_time:
            start_times.append(cur_time)
            cur_time += self.class_duration + self.break_length

        return [ If(And(self.course(i) != 0, self.room(i) != 0, self.teacher(i) != 0), 
                    Or([TimeBlock.start(self.time(i)) == s for s in start_times]),
                    True) 
                 for i in range(self.class_count) ]

    def ensure_lunch_period(self):
        """ returns a list of z3 constraints making sure no class falls within the lunch period """
        return [ If(And(self.course(i) != 0, self.room(i) != 0, self.teacher(i) != 0),
                    Or(TimeBlock.start(self.time(i)) >= self.lunch_end, 
                    TimeBlock.end(self.time(i)) <= self.lunch_start),
                    True) 
                 for i in range(self.class_count) ]

    def prevent_room_time_collision(self):
        """ returns a list of z3 constraints that prevent a room from being assigned to two 
            classes that occur at the same time. Ignores rooms with id == 0 """
        return [ If(And(i != j, self.room(i) == self.room(j), self.room(i) != 0, self.room(j) != 0),
                     Not( Or( And( TimeBlock.start(self.time(i)) <= TimeBlock.start(self.time(j)), 
                                   TimeBlock.end(self.time(i)) >= TimeBlock.end(self.time(j)) ),
                              And( TimeBlock.start(self.time(i)) <= TimeBlock.start(self.time(j)), 
                                   TimeBlock.end(self.time(i)) >= TimeBlock.start(self.time(j)) ),
                              And( TimeBlock.start(self.time(i)) <= TimeBlock.end(self.time(j)),
                                   TimeBlock.end(self.time(i)) >= TimeBlock.end(self.time(j)) ))),  # then
                     True)  # else
                  for i in range(self.class_count) for j in range(self.class_count) ]

    def prevent_teacher_time_collision(self):
        """ returns a list of z3 constraints that prevent a teacher from being assigned to two 
            classes that occur at the same time. Ignores teachers with id == 0 """
        return [ If(And(i != j, self.teacher(i) == self.teacher(j), self.teacher(i) != 0, self.teacher(j) != 0),
                     Not( Or( And( TimeBlock.start(self.time(i)) <= TimeBlock.start(self.time(j)), 
                                   TimeBlock.end(self.time(i)) >= TimeBlock.end(self.time(j)) ),
                              And( TimeBlock.start(self.time(i)) <= TimeBlock.start(self.time(j)), 
                                   TimeBlock.end(self.time(i)) >= TimeBlock.start(self.time(j)) ),
                              And( TimeBlock.start(self.time(i)) <= TimeBlock.end(self.time(j)),
                                   TimeBlock.end(self.time(i)) >= TimeBlock.end(self.time(j)) ))),  # then
                     True)  # else
                  for i in range(self.class_count) for j in range(self.class_count) ]

        # return [ If(And(i != j, self.teacher(i) == self.teacher(j), self.teacher(i) != 0, self.teacher(j) != 0), 
        #             Not(self.time(i) == self.time(j)),
        #             True)
        #         for i in range(self.class_count) for j in range(self.class_count)]

    # 217 seconds
    def prevent_student_time_collision(self):
        """ returns a list of z3 constraints that prevent a student from being assigned to two 
            classes that occur at the same time. Ignores students with id == 0 """
        # x2 = Int(self.next_int_name())   
        # x3 = Int(self.next_int_name())
        # return [If(And(i != j, 
        #            Or(  And( TimeBlock.start(self.time(i)) <= TimeBlock.start(self.time(j)), 
        #                      TimeBlock.end(self.time(i)) >= TimeBlock.end(self.time(j)) ),
        #                 And( TimeBlock.start(self.time(i)) <= TimeBlock.start(self.time(j)), 
        #                      TimeBlock.end(self.time(i)) >= TimeBlock.start(self.time(j)) ),
        #                 And( TimeBlock.start(self.time(i)) <= TimeBlock.end(self.time(j)),
        #                      TimeBlock.end(self.time(i)) >= TimeBlock.end(self.time(j))))),
        #           ForAll([x2, x3], self.students(i)[x2] != self.students(j)[x3]), 
        #           True)
        #         for i in range(self.class_count) for j in range(self.class_count)]
        x = Int(self.next_int_name())   
        y = Int(self.next_int_name())
        return [ForAll([x, y], If(And(x > 0, y > 0, self.students(i)[x] != 0, self.students(j)[y] != 0, 
                                      self.students(i)[x] == self.students(i)[y] ),
                                  Not(Or( And( TimeBlock.start(self.time(i)) <= TimeBlock.start(self.time(j)), 
                                               TimeBlock.end(self.time(i)) >= TimeBlock.end(self.time(j)) ),
                                          And( TimeBlock.start(self.time(i)) <= TimeBlock.start(self.time(j)), 
                                               TimeBlock.end(self.time(i)) >= TimeBlock.start(self.time(j)) ),
                                          And( TimeBlock.start(self.time(i)) <= TimeBlock.end(self.time(j)),
                                               TimeBlock.end(self.time(i)) >= TimeBlock.end(self.time(j))))),
                                 True)) for i in range(self.class_count) for j in range(self.class_count) ]


    def constrain_course_rooms(self):
        """ returns a list of z3 constraints for relationships between courses and rooms. """
        
        cons_models = ClassroomsCourse.query.all()
        cons_list = []
        # we need to construct a big 'OR' clause for each course that has 
        # all the available rooms. We'll restructure the data to make this easier
        mod_map = {}
        for mod in cons_models:
            if mod.course_id not in mod_map:
                mod_map[mod.course_id] = [mod.classroom_id, 0]
            else:
                mod_map[mod.course_id].append(mod.classroom_id)

        # now we can loop through the map's keys and add the constraints
        for course_id in mod_map.keys():

            # the rooms aren't grouped in the DB so we look through all the models and 
            # construct a list of rooms available to this course.
            cons_list += [ If( self.course(i) == course_id, 
                               Or([ self.room(i) == room_id for room_id in mod_map[course_id] ]), 
                               True )  
                            for i in range(self.class_count) for j in range(self.class_count) ]
        return cons_list


    def constrain_min_course_size(self):
        pass
        # TODO
        

        # for course in Course.query.all():
        #     if course.min_student_count:
        #         cons_list += [ If( self.course(i) == course.id, 
        #                            Distinct([ self.students(i)[j] for j in range(max_class_size(self.course(i), self.room(i)))]), 
        #                            True) 
        #                         for i in range(self.class_count)]
            # if course.max_student_count:
            #     cons_list += [ If( self.course(i) == course.id, 
            #                         Not(Distinct([ self.students(i)[j] for j in range(course.max_student_count)])), 
            #                         True) 
            #                     for i in range(self.class_count)]

    def constrain_max_course_size(self):
        """ returns a list of z3 constraints for min and max student count on each course. 
            Ignores courses and rooms with id == 0 """
        
        course_ids = [ c.id for c in Course.query.all() ]
        room_ids = [ r.id for r in Classroom.query.all() ]
        cons_list = []

        # We force the student ids to be zero after the max size
        for course_id in course_ids:
            for room_id in room_ids:
                x = Int(self.next_int_name())
                cons_list += [ If( And(self.course(i) == course_id, self.room(i) == room_id ),
                                    ForAll([x], If( x > self.max_class_size(course_id, room_id), 
                                                    self.students(i)[x] == 0,
                                                    True)),
                                    True)
                                for i in range(self.class_count) ]

        return cons_list

    def constrain_student_courses(self):
        """ returns a list of z3 constraints for courses a student must take """

        cons_list = []
        # constraints of students to courses can come as direct relationships between students and 
        # courses, or by the student being a member of a student group that has a constraint 
        # relationship with the course. 
        for cs in CoursesStudent.query.all():
            # print('\033[94m CS-REQ Course: \033[0m student: {} course: {}'.format(cs.student_id, cs.course_id), file=sys.stderr)
            # or_list = []
            # for i in range(self.class_count):
            #     x = Int(self.next_int_name())

            #     or_list += [ And(self.course(i) == cs.course_id, 
            #                      self.students(i)[x] == cs.student_id,
            #                      x <= self.max_class_size(cs.course_id),
            #                      x > 0,
            #                      self.room(i) != 0,
            #                      self.teacher(i) != 0) ]

            # cons_list += [ Or(or_list) ] 
            cons_list += [ Or([ And(self.course(i) == cs.course_id, 
                                 Or([ self.students(i)[x] == cs.student_id 
                                      for x in range(self.max_class_size(cs.course_id)) ]),
                                 self.room(i) != 0,
                                 self.teacher(i) != 0)
                           for i in range(self.class_count)]) ]

        # include classes assigned to the student group
        for cgrp in CoursesStudentGroup.query.all():
            stud_list = cgrp.student_group.students
            for stud in stud_list:
                # print('\033[94m CSGRP-REQ Course: \033[0m student: {} course: {}'.format(stud.id, cgrp.course_id), file=sys.stderr)
                # or_list = []
                # for i in range(self.class_count):
                #     x = Int(self.next_int_name())

                #     or_list += [ And(self.course(i) == cgrp.course_id, 
                #                      self.students(i)[x] == stud.id,
                #                      x <= self.max_class_size(cgrp.course_id),
                #                      x > 0,
                #                      self.room(i) != 0,
                #                      self.teacher(i) != 0) ]
                # cons_list += [ Or(or_list) ] 
                cons_list += [ Or([ And(self.course(i) == cgrp.course_id, 
                                     Or([ self.students(i)[x] == stud.id 
                                          for x in range(self.max_class_size(cgrp.course_id)) ]),
                                    self.room(i) != 0,
                                    self.teacher(i) != 0)
                               for i in range(self.class_count)]) ]


        return cons_list

    def constrain_room_time(self):
        """ 
        returns a list of z3 constrains that prevent a room from being scheduled beyond 
        its available start and end times 
        """
        cons_list = []
        for room in Classroom.query.all():
            if room.avail_start_time:
                cons_list += [ If(And(self.room(i) == room.id, self.teacher(i) != 0, self.course(i) != 0),
                                   TimeBlock.start(self.time(i)) >= room.avail_start_time,
                                   True ) for i in range(self.class_count) ]
            if room.avail_end_time:
                cons_list += [ If(And(self.room(i) == room.id, self.teacher(i) != 0, self.course(i) != 0),
                                  TimeBlock.end(self.time(i)) <= room.avail_end_time,
                                  True) for i in range(self.class_count) ]

        return cons_list

    def constrain_teacher_time(self):
        """ 
        returns a list of z3 constrains that prevent a room from being scheduled beyond 
        its available start and end times 
        """
        cons_list = []
        for teach in Teacher.query.all():
            if teach.avail_start_time:
                cons_list += [ If(And(self.teacher(i) == teach.id, self.room(i) != 0, self.course(i) != 0),
                                   TimeBlock.start(self.time(i)) >= teach.avail_start_time,
                                   True ) for i in range(self.class_count) ]
            if teach.avail_end_time:
                cons_list += [ If(And(self.teacher(i) == teach.id, self.room(i) != 0, self.course(i) != 0),
                                  TimeBlock.end(self.time(i)) <= teach.avail_end_time,
                                  True) for i in range(self.class_count) ]

        return cons_list

    def constrain_course_time(self):
        """ 
        returns a list of z3 constrains that prevent a course from being scheduled beyond 
        its available start and end times 
        """
        cons_list = []
        for course in Course.query.all():
            if course.avail_start_time:
                cons_list += [ If(And(self.course(i) == course.id, self.room(i) != 0, self.teacher(i) != 0),
                                   TimeBlock.start(self.time(i)) >= course.avail_start_time,
                                   True ) for i in range(self.class_count) ]
            if course.avail_end_time:
                cons_list += [ If(And(self.course(i) == course.id, self.room(i) != 0, self.teacher(i) != 0),
                                  TimeBlock.end(self.time(i)) <= course.avail_end_time,
                                  True) for i in range(self.class_count) ]

        return cons_list

    def constrain_student_subjects(self):
        """
        returns a list of z3 constraints that ensure a student is enrolled in a course 
        that is part of the subject
        """
        cons_list = []
        for stud_subj in StudentsSubject.query.all():
            or_list = []
            course_subs = CoursesSubject.query.filter_by(subject_id=stud_subj.subject_id).all()
            # print('\033[94m CSSUB-REQ: \033[0m student: {} courses: {}'.format(
            #       stud_subj.student_id, [ cs.id for cs in course_subs]), file=sys.stderr)
            for cs in course_subs:
                or_list += [ Or([ And(self.course(i) == cs.course_id, 
                                     Or([ self.students(i)[x] == stud_subj.student_id 
                                          for x in range(self.max_class_size(cs.course_id)) ]),
                                     self.room(i) != 0,
                                     self.teacher(i) != 0,
                                     TimeBlock.start(self.time(i)) >= 0,
                                     TimeBlock.end(self.time(i)) <= 2359)
                               for i in range(self.class_count)]) ]

            cons_list += [ Or(or_list) ] 
        return cons_list

    def constrain_student_group_subjects(self):
        """
        returns a list of z3 constraints that ensure a student is enrolled in a course 
        that is part of the subject
        """
        cons_list = []
        for sgrp_sub in StudentGroupsSubject.query.all():
            for stud in sgrp_sub.student_group.students:
                or_list = []
                course_subs = CoursesSubject.query.filter_by(subject_id=sgrp_sub.subject_id).all()
                # print('\033[94m CSSUB-REQ: \033[0m student: {} courses: {}'.format(
                #       stud.id, [ cs.id for cs in course_subs]), file=sys.stderr)
                for cs in course_subs:
                    or_list += [ Or([ And(self.course(i) == cs.course_id, 
                                         Or([ self.students(i)[x] == stud.id 
                                              for x in range(self.max_class_size(cs.course_id)) ]),
                                         self.room(i) != 0,
                                         self.teacher(i) != 0,
                                         TimeBlock.start(self.time(i)) >= 0,
                                         TimeBlock.end(self.time(i)) <= 2359)
                                   for i in range(self.class_count)]) ]

                cons_list += [ Or(or_list) ] 
        return cons_list

    def constrain_course_teachers(self):
        cons_list = []
        
        # build a list of courses each teacher can teach
        ct_map = {}
        for ct in CoursesTeacher.query.all():
            if ct.course_id in ct_map:
                ct_map[ct.course_id].append(ct.teacher_id)
            else:
                ct_map[ct.course_id] = [ct.teacher_id]

        # now make the constraint
        for c_id, t_id_list in ct_map.items():
            cons_list += [ If(And(self.course(i) == c_id, self.room(i) != 0),
                              Or([ self.teacher(i) == t_id for t_id in t_id_list]), 
                              True) 
                           for i in range(self.class_count) ]

        return cons_list
    
    def make_schedule(self):
        san_check_start = time.time()
        print('\033[93m Starting sanity check...\033[0m')
        self.check_student_reqs()        
        if len(self.errors) > 0:
            print('\033[91m Sanity check failed ({} errors.)\033[0m'.format(len(self.errors)))

            for err_msg in self.errors:
                print('\033[91m Error: {}\033[0m'.format(err_msg))
            # return 

        timing_start = time.time()
        print('\033[93m Done ({} sec). Preparing constraints...\033[0m'.format(timing_start - san_check_start))
        constraints = []
        
        # these ones are relatively fast (1x)
        constraints += self.ensure_valid_ids()
        constraints += self.ensure_valid_times()
        constraints += self.ensure_valid_class_durations()
        constraints += self.ensure_valid_class_start_times()
        constraints += self.ensure_lunch_period()
        constraints += self.constrain_course_rooms()
        constraints += self.constrain_room_time()
        constraints += self.constrain_course_time()
        constraints += self.constrain_teacher_time()
        constraints += self.constrain_student_subjects()
        constraints += self.constrain_course_teachers()

        # # # # 6x slower
        constraints += self.prevent_room_time_collision()
        constraints += self.prevent_teacher_time_collision() 
        constraints += self.constrain_student_courses()

        # # # 10x slower
        constraints += self.constrain_student_group_subjects()
        
        # # # 42x slower
        constraints += self.prevent_student_time_collision()
        # ?
        # constraints += self.constrain_max_course_size() 



      

        # Finally, ask the solver to give us a schedule and then parse the results
        s = Solver()
        s.set(timeout=21600000) # 21600000 = 6 hrs
        # s.set(verbose=10)
        timing_cons_start = time.time()
        print('\033[93m Constraints prepped in {} s, adding to solver...\033[0m'.format(timing_cons_start - timing_start))
        s.add(constraints)
        timing_check_start = time.time()
        # print('\033[93m Constraints added in {} s, checking Sat...\033[0m'.format(timing_check_start - timing_cons_start))
        tries_left = 3
        is_sat = False
        while tries_left > 0 and not is_sat:
            if s.check() == sat:
                is_sat = True
                break
            else:
                print('\033[91m No sat ({} sec), trying again...\033[0m'.format(time.time() - timing_check_start))
                timing_check_start = time.time()
                tries_left -= 1

        if not is_sat:
            print('\033[91m NO SOLUTION\033[0m')
            raise SchedulerNoSolution()
        else:
            print('\033[92m Satisfied! generating model...\033[0m')
            m = s.model()
            
            # first, make the schedule object and then assign the classes to it
            new_schedule = Schedule(name="Sample Schedule")
            db.session.add(new_schedule)
            db.session.flush() 

            print('Key:', file=sys.stderr)
            print('courses:')
            for c in Course.query.all():
                print('{} = {}'.format(c.id, c.name))

            print('\033[95m course_id | room_id | teacher_id | start_time | end_time \033[0m', file=sys.stderr)

            for i in range(self.class_count):
                course_id = int(str(m.evaluate(self.course(i))))
                room_id = int(str(m.evaluate(self.room(i))))
                teacher_id = int(str(m.evaluate(self.teacher(i))))

                # the id's could be set to 0. we'll skip this course if this is the case
                if course_id == 0 or room_id == 0 or teacher_id == 0:
                    continue

                start_time = int(str(m.evaluate(TimeBlock.start(self.time(i)))))
                end_time = int(str(m.evaluate(TimeBlock.end(self.time(i)))))
                
                
                PRINTC = '\033[92m'
                # if course_id == 0 or room_id == 0 or teacher_id == 0 or start_time < 0 or end_time > 2359:
                #     PRINTC = '\033[91m'
                # else:
                print(PRINTC + '     {}     |    {}    |      {}     |     {}     |    {}\033[0m'.format(
                    course_id, room_id, teacher_id, start_time, end_time), file=sys.stderr)

                if course_id != 0 and room_id != 0 and teacher_id != 0 and start_time >= 0 and end_time <= 2359:
                    c = ScheduledClass(new_schedule.id,
                                       course_id,
                                       room_id,
                                       teacher_id,
                                       start_time,
                                       end_time)
                    db.session.add(c)
                    db.session.flush() 

                # # now add the students to the new class. the z3 arrays are undefined length (they will return values
                # # for any index we give them.) we'll pull values until the max class size after that the values should
                # # voilate the unique constraint.
                student_ids = []
                max_stud_count = self.max_class_size(str(m.evaluate(self.course(i))), int(str(m.evaluate(self.room(i)))))
                for j in range(max_stud_count+5):
                    stud_id = int(str(m.evaluate(self.students(i)[j])))
                    # student_ids.append(stud_id)

                    if stud_id != 0 and stud_id not in student_ids:
                        student_ids.append(stud_id)
                        if course_id != 0 and room_id != 0 and teacher_id != 0 and start_time >= 0 and end_time <= 2359:
                            class_student = ScheduledClassesStudent(student_id=stud_id, scheduled_class_id=c.id)
                            db.session.add(class_student) 
                
                print('students: {}'.format(student_ids))
                db.session.commit()
        timing_end = time.time()
        print('\033[93m check took {} s\033[0m'.format(timing_end - timing_check_start), file=sys.stderr)


