import random
from z3 import *
from schoolbloc.scheduler.models import *
from schoolbloc.config import config
from schoolbloc.scheduler.schedule_data import ScheduleClass, ScheduleStudent, ScheduleData
from schoolbloc.scheduler.schedule_constraints import ScheduleConstraints
from schoolbloc.scheduler.class_constraint import ClassConstraint
import time
import schoolbloc.scheduler.scheduler_util as SchedUtil

class SchedulerNoSolution(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.value)

class Scheduler():

    def __init__(self):

        self.classes = []
        self.sched_students = []
        # self.req_courses = {}

        # a dictionary of ClassConstraint objects. the key's are the course_id
        self.class_constraints = {}

        self.custom_constraints = []
        # Next, ask z3 for a configuration of course, teacher, room, and time.
        self.solver = Solver()
        self.solver.set(timeout=300000) # 5 min

    def __repr__(self):
        return "<day_start_time={} day_end_time={} break_length={} lunch_start={} lunch_end={} class_duration={}>".format(
            self.day_start_time, self.day_end_time, self.break_length, self.lunch_start, self.lunch_end, self.class_duration)


    def max_class_size(self, course_id=None):
        max_count = config.default_max_class_size

        if course_id: 
            course = Course.query.get(course_id)
        else:
            course = None

        if course and course.max_student_count:
            max_count = course.max_student_count

        return max_count

    def min_class_size(self, course_id=None):
        min_count = config.default_min_class_size

        if course_id: 
            course = Course.query.get(course_id)
        else:
            course = None

        if course and course.min_student_count:
            min_count = course.min_student_count

        return min_count

    

    def gen_sched_classes(self, model, sched_constraints):

        sch_map = {}
        # print("\033[92m Gen Schedule------------------------------------\33[0m")
        # print("class constraints")
        # real_class_count = 0
        # const_course_list = []
        # for course_id, const_list in sched_constraints.class_constraints.items():
        #     const_course_list += [ course_id for i in range(len(const_list)) ]
        #     real_class_count += len(const_list)
        # print(const_course_list)
        # print("real class count = {}".format(real_class_count))



        #print('\033[95m course_id | room_id | teacher_id | time_block \033[0m', file=sys.stderr)
        
        class_list = []
        for i in range(sched_constraints.class_count):
            course_id = int(str(model.evaluate(sched_constraints.course(i))))
            room_id = int(str(model.evaluate(sched_constraints.room(i))))
            teacher_id = int(str(model.evaluate(sched_constraints.teacher(i))))
            time_block_index = int(str(model.evaluate(sched_constraints.time(i))))

            #print('\033[92m     {}     |    {}    |      {}     |     {} \033[0m'.format(
            #      course_id, room_id, teacher_id, time_block_index), file=sys.stderr)

            class_list.append(ScheduleClass(course_id,
                                            room_id,
                                            teacher_id,
                                            time_block_index,
                                            self.max_class_size(course_id),
                                            self.min_class_size(course_id)))

        sched_data = ScheduleData(class_list)
        # print("schedule data")
        # print("class course ids: {}".format([ c.course_id for c in class_list]))
        # print("result count = {}".format(len(class_list)))
        # print("\033[92m end------------------------------------\33[0m")

        return sched_data

    def make_schedule(self):
        
        SchedUtil.log_note("info", "Scheduler", "Scheduler started")
        # first step, decide how many classes of each course we need
        # this is decided based on the need of the students, and what 
        # teachers and rooms are available for each course.
        sched_constraints = ScheduleConstraints()

        # try a bunch of times before resorting to adding a class
        # attempts = int(len(sched_constraints.student_requirement_set) / 10)
        self.solver.push()

        for i in range(50):
            start_time = time.time()
            collisions = []
            
            SchedUtil.log_note("info", "Scheduler", "Attempting to solve using {} classes".format(sched_constraints.class_count))
            for i in range(20): # try 20 different z3 mappings
            # find a valid z3 mapping, or quit because none exist
                SchedUtil.log_note("info", "Scheduler", "Generating a mapping of teachers, courses, classrooms and timeblocks")
                while True:
                    self.set_constraints(sched_constraints.get_constraints())
                    if self.solver.check() != sat:
                        SchedUtil.log_note("warning", "Scheduler", "Solver could not find a solution for the current constraint set")
                    
                        if sched_constraints.can_relax_constraints():
                            sched_constraints.relax_constraints()
                            sched_constraints.reset_constraints()
                        else:
                            SchedUtil.log_note("error", "Scheduler", "No valid mapping exists for current constraint set")
                            raise SchedulerNoSolution('Not satisfiable')
                    else:
                        SchedUtil.log_note("info", "Scheduler", "Valid mapping found, attempting to schedule students")
                        break

                schedule = self.gen_sched_classes(self.solver.model(), sched_constraints)
                # now start assigning students to classes and see if we can find
                # a place for every student
                collisions = self.place_students(schedule, sched_constraints.student_requirement_set)
                if len(collisions) == 0:
                    SchedUtil.log_note("success", "Scheduler", "Solution found, saving schedule now")
                    schedule.save()
                    return
                else:
                    if i < 20:
                        SchedUtil.log_note("warning", "Scheduler", "Failed placing students, attempting again with a new mapping")

            # end_time = time.time()
            if sched_constraints.can_relax_constraints():
                SchedUtil.log_note("warning", "Scheduler", "Failed placing students, relaxing constraints and trying again")
                sched_constraints.relax_constraints()
                sched_constraints.reset_constraints()    
            else:
                SchedUtil.log_note("warning", "Scheduler", "Failed placing students, adding another class and trying again")
                sched_constraints.add_class_from_collisions(collisions)

        SchedUtil.log_note("error", "Scheduler", "Scheduler failed to place students")
        raise SchedulerNoSolution()

    def set_constraints(self, constraints):
        self.solver.pop() # pop off the constraints so we can reset them
        self.solver.push() # push a new 'constraint frame' so we can pop it later if needed
        self.solver.add(constraints)


    def place_students(self, schedule, student_requirement_set):
        """
        Attempts to place all the students in the schedule. This method will try to place the student
        and if it fails, it will call a method to add targeted constraints then try placing the students again.

        :param schedule: the ScheduleData constructed out of the z3
        :param student_requirement_set:
        :return: True if successfully placed all students, False otherwise
        """
        # try every order of placing students, if they all fail, add constraints and try again
        all_collisions = []
        for i in range(len(student_requirement_set)):
            for student_reqs in student_requirement_set:
                # print("placing student {}".format(student_reqs.student_id))
                collisions = schedule.schedule_student(student_reqs.student_id,
                                                      student_reqs.required_course_ids,
                                                      student_reqs.optional_course_ids)
                if len(collisions) > 0:
                    # print('\033[91m Failed on student {}, reordering student list and trying again...\033[0m'.format(
                    #     student_reqs.student_id))
                    schedule.clear_all_students()
                    all_collisions += collisions

                    break
            # if we placed every student then return an empty list indicating success
            if len(all_collisions) == 0:
                return []

        return all_collisions
