from z3 import *
from schoolbloc.scheduler.models import *
from schoolbloc.config import config
from schoolbloc.scheduler.schedule_util import ScheduleClass, ScheduleStudent, ScheduleData
from schoolbloc.scheduler.schedule_constraints import ScheduleConstraints, ClassConstraint
from functools import wraps
import time





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

    def __init__(self):

        self.class_count = 0
        self.classes = []
        self.sched_students = []
        # self.req_courses = {}

        # a dictionary of ClassConstraint objects. the key's are the course_id
        self.class_constraints = {}

        self.custom_constraints = []


    def __repr__(self):
        return "<day_start_time={} day_end_time={} break_length={} lunch_start={} lunch_end={} class_duration={}>".format(
            self.day_start_time, self.day_end_time, self.break_length, self.lunch_start, self.lunch_end, self.class_duration)


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
        
        class_size = config.default_max_class_size

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

    

    def gen_sched_classes(self, model, class_count, sched_constraints):

        sch_map = {}

        print('\033[95m course_id | room_id | teacher_id | time_block \033[0m', file=sys.stderr)
        
        class_list = []
        for i in range(class_count):
            course_id = int(str(model.evaluate(sched_constraints.course(i))))
            room_id = int(str(model.evaluate(sched_constraints.room(i))))
            teacher_id = int(str(model.evaluate(sched_constraints.teacher(i))))
            time_block_index = int(str(model.evaluate(sched_constraints.time(i))))

            print('\033[92m     {}     |    {}    |      {}     |     {} \033[0m'.format(
                  course_id, room_id, teacher_id, time_block_index), file=sys.stderr)

            class_list.append(ScheduleClass(course_id,
                                            room_id,
                                            teacher_id,
                                            time_block_index,
                                            self.max_class_size(course_id, room_id),
                                            0))

        timeblocks = Timeblock.query.all()
        return ScheduleData(class_list, timeblocks)


    def make_schedule(self):
        
        # first step, decide how many classes of each course we need
        # this is decided based on the need of the students, and what 
        # teachers and rooms are available for each course.

        # figure out how many time blocks we have in a day and get an array
        # of them. the index of the array represents the id of the time block 
        # for z3 
        sched_constraints = ScheduleConstraints()
        class_count = sched_constraints.class_count

        # We'll add all the constraints (implied and user provided). 
        # timing_start = time.time()

        # Next, ask z3 for a configuration of course, teacher, room, and time.
        solver = Solver()
        solver.set(timeout=300000) # 5 min
        solver.push()

        
        attempts = 3
        for i in range(attempts):
            solver.push()
            solver.add(sched_constraints.constraints)

            if solver.check() != sat:
                # pop the current constraints and add another class. then recalculate the constraints
                solver.pop()
                solver.push()
                print('\033[91m No sat, trying again with {} classes...\033[0m'.format(class_count))
                solver.add(sched_constraints.constraints)
                continue
            else:
                schedule = self.gen_sched_classes(solver.model(), class_count, sched_constraints)
            # now start assigning students to classes and see if we can find
            # a place for every student
            collisions = self.place_students(schedule, sched_constraints.student_requirement_set)
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
                print('\033[91m Failed placing students, trying again...\033[0m')
                sched_constraints.gen_constraints_from_collisions(collisions)
                # send response constraints to be included in DB generated constraints
                solver.add(sched_constraints.constraints)

        print('\033[91m NO SOLUTION\033[0m')
        raise SchedulerNoSolution()


    def place_students(self, schedule, student_requirement_set):
        collisions = []
        for student_reqs in student_requirement_set:
            collision = schedule.schedule_student(student_reqs.student_id, 
                                                  student_reqs.required_course_ids, 
                                                  student_reqs.optional_course_ids)
            if collision:
                collisions.append(collision)
                return collisions
        return collisions
    

            
    def save_schedule(self):
        db_schedule = Schedule(name="Sample Schedule")
        db.session.add(db_schedule)
        db.session.flush()
        schedule.save(db_schedule, db, self.time_blocks)
