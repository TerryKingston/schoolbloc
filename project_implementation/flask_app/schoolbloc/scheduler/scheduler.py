from z3 import *
from schoolbloc.scheduler.models import *
from schoolbloc import db
from schoolbloc.config import config
from schoolbloc.scheduler.schedule_util import Schedule as ScheduleData
from schoolbloc.scheduler.schedule_util import ScheduleClass 
from schoolbloc.scheduler.schedule_util import Student as ScheduleStudent
from functools import wraps
import time

DEFAULT_MAX_CLASS_SIZE = 29

# make the class z3 data type and define its constructor
# a class represents a mapping of teacher, room, course, time, and students
# Z3 will choose integers for teacher, room, course, and time. Its our job to
# restrict the choices of integer to only valid IDs of correspoding DB objects
SchClass = Datatype('SchClass')

SchClass.declare('SchClass', ('teacher', IntSort()),
                             ('room', IntSort()),
                             ('time', IntSort()),
                             ('course', IntSort()))

SchClass = SchClass.create()

class TimeBlock():
    """
    Helper class to hold time block data
    """
    def __init__(self, start, end):
        self.start = start
        self.end = end

# class SchedulerStudent():
#     """
#     Helper class used to hold the student schedule info when trying to make a valid schedule
#     """
#     def __init__(self, student_id):
#         self.student_id = student_id
#         self.req_course_ids = [] # a list of id's of courses needed by the student
#         self.sch_classes = [] # the scheduled classes the student is assigned to

#     def add_class(self, sch_class):
#         """
#         Attempts to add the sch_class to the student. if the student is already
#         assigned to a class with the same time block the class is not added and False 
#         is returned. else, the schedule is added and True is returned
#         """
#         if self.is_time_taken(sch_class.time_block_index):
#             return False
#         else:
#             self.sch_classes.push(sch_class)
#             return True

#     def drop_class(self, sched_class):
#         """
#         Drops the sch_class from the student if it has been assigned
#         """
#         for i in len(range(self.sched_classes)):
#             if self.sched_classes[i].time_block_index == time_block_index:
#                 self.sched_classes.pop(i)
#                 return True
#         return False

#     def is_time_taken(self, time_block_index):
#         for c in self.sched_classes:
#             if c.time_block_index == time_block_index:
#                 return True
#         return False

class SchedulerNoSolution(Exception):
    pass

class Scheduler():

    def place_student(self, sch_class_map, sch_student):

        # go through each course assigned to the student and 
        # try to place them in one of the scheduled classes
        # for that course
        return self.assign_class_for_course(sch_class_map, sch_student, 0)


    def assign_class_for_course(self, sch_class_map, sch_student, course_index):
        """
        Recursively assigns the SchedulerStudent to all of its required courses (which are
        defined by the req_course_ids property.)

        sch_class_map = a map of ScheduledClass objects (i.e. {course_id => [<ScheduledClass>, <ScheduledClass> ...]} )
        sch_student = ScheduerStudent object being assigned to courses
        course_index = index into sch_student.req_course_ids for the current course being assigned
        """
        if course_index >= len(sch_student.req_course_ids):
            return True
        
        # loop through the list of scheduled classes for each course
        # to find one that is free
        course_id = sch_student.req_course_ids[course_index]
        for sch_class in sch_class_map[course_id]:
            # if the time block for this class is not already 
            # filled with something else for this student, then use
            # this class and recursively assign the next class
            if sch_student.add_class(sch_class):
                if assign_class_for_course(sch_student, course_index + 1):
                    return True
                else:
                    sch_student.drop_class(sch_class)
            # else, try the next class

        # If we didn't find any classes that would work then return false
        return False

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

    

    def __init__(self, day_start_time=None, 
                       day_end_time=None, 
                       break_length=None, 
                       lunch_start=None, 
                       lunch_end=None,
                       class_duration=None):

        # if values aren't provided, get the defaults from the config file
        self.day_start_time = day_start_time or config.school_start_time
        self.day_end_time = day_end_time or config.school_end_time
        self.break_length = break_length or config.time_between_classes
        self.lunch_start = lunch_start or config.lunch_start
        self.lunch_end = lunch_end or config.lunch_end
        self.class_duration = class_duration or config.block_size

        self.class_count = 0
        self.classes = []
        self.sched_students = []
        self.req_courses = {}

        # calculate the timeblocks
        self.time_blocks = []
        self.calc_time_blocks()


    def __repr__(self):
        return "<day_start_time={} day_end_time={} break_length={} lunch_start={} lunch_end={} class_duration={}>".format(
            self.day_start_time, self.day_end_time, self.break_length, self.lunch_start, self.lunch_end, self.class_duration)

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

    def calc_time_blocks(self):
        """
        Creates a list of TimeBlock objects and stores them in self.time_block. 
        The TimeBlock start and end times are calculated based on the Scheduler attributes
        day_start_time, class_duration, break_length, lunch_start, lunch_end, and day_end_time 
        """
        self.time_blocks = []
        cur_time = self.day_start_time
        while cur_time < self.lunch_start:
            self.time_blocks.append(TimeBlock(cur_time, cur_time + self.class_duration))
            cur_time += self.class_duration + self.break_length

        cur_time = self.lunch_end
        while cur_time < self.day_end_time:
            self.time_blocks.append(TimeBlock(cur_time, cur_time + self.class_duration))
            cur_time += self.class_duration + self.break_length

    def calc_req_courses(self):
        """
        Calculates the courses needed from the required corses for each student.
        In the case of a Subject requirement, without a course requirement for the 
        Subject, a course is arbritrarily assigned. 

        Also, this method creates a list of SchedulerStudent objects with their required
        course ids. It also detects when
        a student is assigned to more courses than there are time_blocks in the schedule
        """
        self.req_courses = {}
        self.sched_students = []

        for student in Student.query.all():
            req_courses = self.calc_student_courses(student.id)
            sched_student = ScheduleStudent(student.id, len(self.time_blocks), req_courses, [])
            self.sched_students.append(sched_student)

            if len(req_courses) > len(self.time_blocks):
                msg = "Student {} course req ({}) is greater than time block count ({})".format(
                    student.id, len(req_courses), len(self.time_blocks))
                raise SchedulerNoSolution(msg)
            else:
                for course_id in req_courses:
                    if course_id in self.req_courses:
                        self.req_courses[course_id].append(student.id)
                    else:
                        self.req_courses[course_id] = [student.id]

        # now we know how many students are assigned to each course. we'll go through each 
        # and determine the total course count from the max student count of each course
        self.class_count = 0
        for c_id, stud_list in self.req_courses.items():
            max_stud_count = self.max_class_size(c_id)
            self.class_count += int(len(stud_list) / max_stud_count)
            # if it didn't divide cleanly, then add 1 more class for that course
            if len(stud_list) % max_stud_count != 0:
                self.class_count += 1


    @classmethod
    def calc_student_courses(self, student_id):
        """
        Calculates the courses needed from the required corses for the student.
        In the case of a Subject requirement, without a course requirement for the 
        Subject, a course is arbritrarily assigned. This method also detects when
        a student is assigned to more courses than there are time_blocks in the schedule
        """
        required_course_ids = []
        for course_student in CoursesStudent.query.filter_by(student_id=student_id).all():
            required_course_ids.append(course_student.course_id)


        # now add the courses that are required for all the student groups this student
        # is part of
        for sgrp in StudentsStudentGroup.query.filter_by(student_id=student_id).all():
            for course_sgrp in CoursesStudentGroup.query.filter_by(student_group_id=sgrp.student_group_id):
                
                if course_sgrp.course_id not in required_course_ids:
                    required_course_ids.append(course_sgrp.course_id)

            # and pick a course in the subjects required for the student group
            for sub_sgrp in StudentGroupsSubject.query.filter_by(student_group_id=sgrp.student_group_id).all():
                cs_subs = CoursesSubject.query.filter_by(subject_id=sub_sgrp.subject_id).all()
                if len(cs_subs) > 0:
                    course_ids = [ cs.course_id for cs in cs_subs ]
                    # if we don't already have a course for this subject then pick one and add it
                    intersect = set(course_ids) & set(required_course_ids)
                    # intersect = [ filter(lambda x: x in course_ids, sublist) for sublist in required_course_ids ]
                    if len(intersect) == 0:
                        required_course_ids.append(course_ids[0])


        # pick a course in the subjects required for the student
        for sub_stud in StudentsSubject.query.filter_by(student_id=student_id).all():
            cs_subs = CoursesSubject.query.filter_by(subject_id=sub_stud.subject_id).all()
            if len(cs_subs) > 0:
                course_ids = [ cs.course_id for cs in cs_subs ]
                # if we don't already have a course for this subject then pick one and add it
                intersect = set(course_ids) & set(required_course_ids)
                if len(intersect) == 0:
                    required_course_ids.append(course_ids[0])

        return required_course_ids

    def prep_z3_classes(self):
        self.classes = [Const("class_%s" % (i + 1), SchClass) for i in range(self.class_count)]  

    # ensures the teacher, room, and course ids are valid. We also allow an id
    # of 0 which means null was chosen by the scheduler
    def ensure_valid_ids(self):

        teacher_ids = [t.id for t in Teacher.query.all()]
        room_ids = [r.id for r in Classroom.query.all()]
        course_ids = [c.id for c in Course.query.all()]
        # this basically loops through each class, and then each of the lists above and makes
        # an 'assert equal' for each. The lists are put in an 'Or' constraint to ensure
        # each entry appears in the respective id list
        return [ And(Or([self.teacher(i) == t_id for t_id in teacher_ids]),
                          Or([self.room(i) == r_id for r_id in room_ids]),
                          And(self.time(i) >= 0, self.time(i) < len(self.time_blocks)),
                          Or([self.course(i) == c_id for c_id in course_ids]))
                      for i in range(self.class_count) ]

    def set_courses(self):
        """
        Returns a list of z3 constraints that make sure the scheduler includes the 
        courses we need as determined by calc_req_courses (stored in self.req_courses)
        """
        cons_list = []
        class_index = 0
        # loop through set courses and add constraints for each course
        for c_id, stud_list in self.req_courses.items():
            count = 0
            max_stud_count = self.max_class_size(c_id)
            count += int(len(stud_list) / max_stud_count)
            # if it didn't divide cleanly, then add 1 more class for that course
            if len(stud_list) % max_stud_count != 0:
                count += 1

            for c in range(count):
                cons_list += [ self.course(class_index) == c_id ]
                class_index += 1

        return cons_list


    def prevent_room_time_collision(self):
        """ returns a list of z3 constraints that prevent a room from being assigned to two 
            classes that occur at the same time. Ignores rooms with id == 0 """
        return [ If(And(i != j, self.room(i) == self.room(j)),
                     self.time(i) != self.time(j), True)
                  for i in range(self.class_count) for j in range(self.class_count) ]

    def prevent_teacher_time_collision(self):
        """ returns a list of z3 constraints that prevent a teacher from being assigned to two 
            classes that occur at the same time. Ignores teachers with id == 0 """
        return [ If(And(i != j, self.teacher(i) == self.teacher(j)),
                    self.time(i) != self.time(j), True)
                  for i in range(self.class_count) for j in range(self.class_count) ]

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
        if len(ct_map) == 0:
            return cons_list

        for c_id, t_id_list in ct_map.items():
            cons_list += [ If(self.course(i) == c_id,
                              Or([ self.teacher(i) == t_id for t_id in t_id_list]), 
                              True) 
                           for i in range(self.class_count) ]

    def calc_avail_time_ids(self, start_time=None, end_time=None):
        times = []
        for i in range(self.time_blocks):
            time_block = self.time_blocks[i]
            if start_time and end_time:
                if start_time >= time_block.start and end_time <= time_block.end:
                    times.append(i)
            elif start_time:
                if start_time >= time_block.start:
                    times.append(i)
            elif end_time:
                if end_time <= time_block.end:
                    times.append(i)
            else:
                times.append(i)


    def constrain_room_time(self):
        """ 
        returns a list of z3 constrains that prevent a room from being scheduled beyond 
        its available start and end times 
        """

        cons_list = []
        for room in Classroom.query.all():
            if not room.avail_start_time and not room.avail_end_time:
                continue
            # figure out which time blocks can be assigned to the room
            avail_time_ids = self.calc_avail_time_ids(room.avail_start_time, room.avail_end_time)
            
            cons_list += [ If(self.room(i) == room.id, 
                              Or([ self.time(i) == time_id for time_id in avail_time_ids ]),
                              True)
                           for i in range(self.class_count) ]

        return cons_list
    
    def constrain_teacher_time(self):
        """ 
        returns a list of z3 constrains that prevent a teacher from being scheduled beyond 
        his/her available start and end times 
        """

        cons_list = []
        for teacher in Teacher.query.all():
            if not teacher.avail_start_time and not teacher.avail_end_time:
                continue
            # figure out which time blocks can be assigned to the teacher
            avail_time_ids = self.calc_avail_time_ids(teacher.avail_start_time, teacher.avail_end_time)
            
            cons_list += [ If(self.teacher(i) == teacher.id, 
                              Or([ self.time(i) == time_id for time_id in avail_time_ids ]),
                              True)
                           for i in range(self.class_count) ]

        return cons_list

    def constrain_course_time(self):
        """ 
        returns a list of z3 constrains that prevent a course from being scheduled beyond 
        its available start and end times 
        """

        cons_list = []
        for course in Teacher.query.all():
            if not course.avail_start_time and not course.avail_end_time:
                continue
            # figure out which time blocks can be assigned to the course
            avail_time_ids = self.calc_avail_time_ids(course.avail_start_time, course.avail_end_time)
            
            cons_list += [ If(self.course(i) == course.id, 
                              Or([ self.time(i) == time_id for time_id in avail_time_ids ]),
                              True)
                           for i in range(self.class_count) ]

        return cons_list


    def gen_sched_classes(self, model):

        sch_map = {}

        print('\033[95m course_id | room_id | teacher_id | time_block \033[0m', file=sys.stderr)
        
        class_list = []
        for i in range(self.class_count):
            course_id = int(str(model.evaluate(self.course(i))))
            room_id = int(str(model.evaluate(self.room(i))))
            teacher_id = int(str(model.evaluate(self.teacher(i))))
            time_block_index = int(str(model.evaluate(self.time(i))))

            print('\033[92m     {}     |    {}    |      {}     |     {} \033[0m'.format(
                  course_id, room_id, teacher_id, time_block_index), file=sys.stderr)

            class_list.append(ScheduleClass(course_id,
                                            room_id,
                                            teacher_id,
                                            time_block_index,
                                            self.max_class_size(course_id, room_id),
                                            0))


        return ScheduleData(class_list)

    def prep_constraints(self, inc_constraints=None):
        constraints = inc_constraints or []
        constraints += self.ensure_valid_ids()
        constraints += self.set_courses()
        constraints += self.prevent_room_time_collision()
        constraints += self.prevent_teacher_time_collision() 

        # # User provided constraints
        constraints += self.constrain_course_rooms()
        constraints += self.constrain_room_time()
        constraints += self.constrain_course_time()
        constraints += self.constrain_teacher_time()
        constraints += self.constrain_course_teachers()
        return constraints

    def make_schedule(self):
        
        # first step, decide how many classes of each course we need
        # this is decided based on the need of the students, and what 
        # teachers and rooms are available for each course.

        # figure out how many time blocks we have in a day and get an array
        # of them. the index of the array represents the id of the time block 
        # for z3 
        self.calc_req_courses()

        print('\033[92m Calculated course Requirements: \033[0m')
        for course_id, stud_list in self.req_courses.items():
            print('\033[92m Course: {} Students: {} \033[0m'.format(
                    course_id, stud_list))

        # if theres not enough teachers and/or rooms to meet the needs
        # of the students we stop here and inform the user
        # TODO

        # We'll add all the constraints (implied and user provided). 
        # timing_start = time.time()

        # Next, ask z3 for a configuration of course, teacher, room, and time.
        solver = Solver()
        solver.set(timeout=300000) # 5 min
        solver.push()
        self.prep_z3_classes()

        
        attempts = 3
        for i in range(attempts):
            solver.push()
            solver.add(self.prep_constraints())

            if solver.check() != sat:
                # pop the current constraints and add another class. then recalculate the constraints
                solver.pop()
                solver.push()
                self.class_count += 1
                print('\033[91m No sat, trying again with {} classes...\033[0m'.format(self.class_count))
                self.prep_z3_classes()
                solver.add(self.prep_constraints())
                continue
            else:
                schedule = self.gen_sched_classes(solver.model())
            # now start assigning students to classes and see if we can find
            # a place for every student
            collisions = self.place_students(schedule)
            if len(collisions) == 0:
                print('\033[92m Satisfied! \033[0m')
                print('\033[92m {} \033[0m'.format(schedule))
                # now save the schedule
                self.save_schedule(schedule)
                return
            else:
                # pop off the constraints so we can reset them
                solver.pop()
                # push a new 'constraint frame' so we can pop it later if needed
                solver.push()
                constraints = self.gen_constraints_from_collisions(collisions)
                print('\033[91m Failed placing students, trying again...\033[0m')
                self.prep_z3_classes()
                # send response constraints to be included in DB generated constraints
                solver.add(self.prep_constraints(constraints))

        print('\033[91m NO SOLUTION\033[0m')
        raise SchedulerNoSolution()

    def place_students(self, schedule):
        collisions = []
        for student in self.sched_students:
            collision = schedule.schedule_student(student)
            if collision:
                collisions.append(collision)
                return collisions

    def gen_constraints_from_collisions(self, collisions):
        for col in collisions:
            msg = "{} collision on student {}".format(col.collision_type, col.student.id)
            print('\033[91m{}\033[0m'.format(msg))
            # now make a constraint to avoid the collision
            if col.collision_type == 'timeblock':
                
            elif col.collision_type == 'full class':
        return []
            
    def save_schedule(self):
        db_schedule = Schedule(name="Sample Schedule")
        db.session.add(db_schedule)
        db.session.flush()
        schedule.save(db_schedule, db, self.time_blocks)
