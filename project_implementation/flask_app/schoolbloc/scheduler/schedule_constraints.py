# from schoolbloc.scheduler.scheduler import SchedulerNoSolution
from z3 import *
from schoolbloc.scheduler.models import *
from schoolbloc.config import config
from schoolbloc.scheduler.class_constraint import ClassConstraint
#from schoolbloc.scheduler.scheduler import SchedulerNoSolution
import math
import time
import schoolbloc.scheduler.scheduler_util as SchedUtil

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

class ScheduleConstraints:
    """
    Manages the set of constraints for the scheduler. This object can create constraints based 
    on the data in the DB
    """
    @staticmethod
    def max_student_count(course_id):
        course = Course.query.get(course_id)
        return course.max_student_count or config.default_max_class_size

    @staticmethod
    def gen_course_path_helper(course_list, current_path, path_list):
        if len(course_list) == 0:
            return
        elif len(course_list) == 1:
            for course_id in course_list[0]:
                # add a copy of the current path with each course_id from the last list
                # appended to the end
                full_path = list(current_path) + [course_id]
                path_list.append(full_path)
        else:
            # else, make a copy of the current path with the course id appended to the end
            # and then move to the next course_id list
            for course_id in course_list[0]:
                new_path = list(current_path) + [course_id]
                ScheduleConstraints.gen_course_path_helper(course_list[1:], new_path, path_list)

    
    @staticmethod
    def gen_course_path_list(course_list):
        """
        generates a list of possible course combinations from the course list. 
        For example, if course_list = [[1, 2, 3], [4], [5, 6]] 
        then the result is: [[1, 4, 5], [1, 4, 6], [2, 4, 5], [2, 4, 6], [3, 4, 5], [3, 4, 6]]
        
        course_list: an array of arrays where each array is the z3 ids of ClassConstraints for a 
                     single course

        """
        path_list = []
        for course_id in course_list[0]:
            ScheduleConstraints.gen_course_path_helper(course_list[1:], [course_id], path_list)

        return path_list

    def __init__(self):
        self.class_count = 0
        self.db_constraints = [] # the list of z3 constraints generated from the DB
        self.course_time_constraints = {} # constraints generated from course-time collisions. student_id => constraint list
        self.course_index_list_cache = []
        self.class_constraints = {}
        self.student_requirement_set = [] # list of StudentRequirement objects

        self.prep_class_constraints()
        self.reset_constraints()


    def get_constraints(self):
        """
        returns the current set of constraints
        """
        constraints = self.db_constraints
        for student_id, const_list in self.course_time_constraints.items():
            constraints += const_list
        return constraints

    def can_relax_constraints(self):
        """
        returns true if the constraints set includes high priority constraints that can fall back 
        onto low priority constraints
        """
        for course_id, class_constraints in self.class_constraints.items():
            for class_constraint in class_constraints:
                if class_constraint.can_relax_constraints():
                    return True

        return False

    def relax_constraints(self):
        #TODO should take a more intellegent approach to this, but for now, blindly grab one and relax it
        for course_id, class_constraints in self.class_constraints.items():
            for class_constraint in class_constraints:
                if class_constraint.can_relax_constraints():
                    class_constraint.relax_constraints()
                    return 


    def prep_z3_classes(self):
        self.z3_classes = [Const("class_%s" % (i + 1), SchClass) for i in range(self.class_count)] 

    def prep_implied_constraints(self):
        self.db_constraints += self.set_courses()
        
        # print('\033[92m class count: {} \033[0m'.format( self.class_count))
        self.check_fact_utilization()
        self.db_constraints += self.prevent_room_time_collision()
        self.db_constraints += self.prevent_teacher_time_collision()
        self.db_constraints += self.ensure_course_timeblock_paths()

    #def prep_db_constraints(self):
    #    self.db_constraints += self.constrain_room_time()
    #    self.db_constraints += self.constrain_teacher_time()

    #   self.db_constraints += self.constrain_course_rooms()
    #    self.db_constraints += self.constrain_course_time()
    #    self.db_constraints += self.constrain_course_teachers()

    def reset_constraints(self):
        """
        Re-calculates the implied constraints and the database constraints
        """
        start_time = time.time()
        self.db_constraints = []
        self.prep_z3_classes()
        self.prep_implied_constraints()
        #self.prep_db_constraints()
        # print("reset constraints ( {} min )".format(round((time.time() - start_time)/60)))

    def prep_class_constraints(self):
        """
        Calculates the classes of each course that will be needed based on 
        """
        self.class_constraints = {}
        self.class_count = 0

        for student in Student.query.all():
            # make a list of the required course ids for the student
            req_courses = self.calc_student_courses(student.id)
            student_reqs = StudentRequirements(student.id, req_courses, [])
            self.student_requirement_set.append(student_reqs)

            # detect if the student is over scheduled
            ScheduleConstraints.check_if_student_is_overscheduled(student, req_courses)
            # now go through the list and create courses when needed
            for course_id in req_courses:
                # max_stud_count = int(ScheduleConstraints.max_student_count(course_id) * .9)
                max_stud_count = int(ScheduleConstraints.max_student_count(course_id))
                course = Course.query.get(course_id)

                if course_id not in self.class_constraints:
                    new_class = ClassConstraint(course_id, course.name)
                    self.class_constraints[course_id] = [new_class]
                    self.class_count += 1
                
                elif self.class_constraints[course_id][0].student_count < max_stud_count:
                    self.class_constraints[course_id][0].student_count += 1
                
                else:
                    new_class = ClassConstraint(course_id, course.name)
                    self.class_constraints[course_id].insert(0, new_class)
                    self.class_count += 1

    @staticmethod
    def check_if_student_is_overscheduled(student, required_courses):
        timeblock_count = Timeblock.query.count()
        if len(required_courses) > timeblock_count:
            msg = "Student {} course requirements ({}) are greater than the available number of timeblocks ({})".format(
                student.id, len(required_courses), timeblock_count)
            SchedUtil.log_note("error", "Scheduler", msg)
            raise SchedulerNoSolution(msg)
        elif len(required_courses) < timeblock_count:
            msg = "Student {} course requirements are less than the number of timeblocks".format(student.id)
            SchedUtil.log_note("warning", "Scheduler", msg)
            
    def gen_constraints_from_collisions(self, collisions):
        # choose the student with the most collisions that doesn't already
        # have a constraint made for them, and make a timeblock
        # constraint to give them a course path
        student_collision_list = {}
        for col in collisions:
            if col.collision_type == 'full class':
                continue
            student_id = col.student.id
            if student_id not in student_collision_list:
                student_collision_list[student_id] = []
            student_collision_list[student_id].append(col)

        best_count = 0
        best_collision = None
        for student_id, coll_list in student_collision_list.items():
            if len(coll_list) > best_count and student_id not in self.course_time_constraints:
                best_collision = coll_list[0]
                best_count = len(coll_list)

        # if we didn't find a best_collision then do nothing
        if best_collision:
            # now make a constraint to avoid the collision
            # self.add_timeblock_constraints_for_student(best_collision.student)
            return True
        else:
            return False

    def add_class_from_collisions(self, collisions):
        """
        Adds a ClassConstraint to the set of class constraints. The course to use for the class is determined
        by the given list of collisions. The most common course among the collisions is used.
        :param collisions: A list of collision objects generated from the last attempt at scheduling
        :return: None (use self.get_constraints() to see the results of this action)
        """
        # find the most popular course among the collisions
        course_collision_list = {}
        for col in collisions:
            if col.collision_type == 'full class':
                continue
            course_id = col.scheduled_class.course_id
            if course_id not in course_collision_list:
                course_collision_list[course_id] = []
            course_collision_list[course_id].append(col)

        best_count = 0
        best_collision = None
        for course_id, coll_list in course_collision_list.items():
            if len(coll_list) > best_count:
                best_count = len(coll_list)
                best_collision = coll_list[0]

        # now add a class for that collisions course
        course_id = best_collision.scheduled_class.course_id
        course = Course.query.get(course_id)
        new_class = ClassConstraint(course_id, course.name)
        self.class_constraints[course_id].append(new_class)
        self.class_count += 1

        msg = "Added another class for the course: {} {}".format(course.id, course.name)
        SchedUtil.log_note("info", "Scheduler", msg)
        self.reset_constraints()


    # def add_class_for_course(self, course_id):
    #     class_const = ClassConstraint(course_id)
    #     # class_const.timeblock_ids = self.calc_avail_timeblocks(course_id)
    #     # class_const.teacher_ids = self.calc_avail_teachers(course_id)
    #     # class_const.room_ids = self.calc_avail_rooms(course_id)
    #
    #     self.class_constraints[course_id].append(class_const)
    #     self.class_count += 1
    #     print('\033[91m Added ClassConstraint: {}\033[0m'.format(class_const))

    def add_timeblock_constraints_for_student(self, student_reqs):
        """
        Go through the courses required by the student and add a constraint that
        prevents timeblock collisions for any of the required courses

        :type student_reqs: StudentRequirements
        :param student_reqs: The set of student requirements for a single student
        :rtype: List
        :return: A list of z3 constraints

        """

        # build a 2 dimensional array representing the z3 indices of the
        # required courses for the student. where the members if each each inner list 
        # represent the same course
        course_indexes = [[ c.z3_index for c in self.class_constraints[course_id] ]
                          for course_id in student_reqs.required_course_ids]

        # cache the course_indexes so we can skip this step when we see duplicates
        for ci in self.course_index_list_cache:
            if course_indexes == ci:
                # print("found duplicate course index list, sikipping student {}".format(student_reqs.student_id))
                return []

        self.course_index_list_cache.append(course_indexes)

        # print('\033[93m course z3 index set:\n {}\033[0m'.format(course_indexes))

        # now generate all the possible course paths for the student
        path_list = ScheduleConstraints.gen_course_path_list(course_indexes)

        # print('\033[93m all possible course paths:\n {}\033[0m'.format(path_list))

        # now build a constraint that ensures at least one arrangement of times for 
        # the courses is free of timeblock collisions
        or_list = []
        for path in path_list:
            and_list = []
            for i in range(len(path)):
                for j in range(len(path)):
                    if i != j:
                        and_list += [ self.time(path[i]) != self.time(path[j]) ]
            or_list += [ And(and_list) ]

        return [Or(or_list)]
        # if student_reqs.id not in self.course_time_constraints:
        #     self.course_time_constraints[student_reqs.id] = []
        # self.course_time_constraints[student_reqs.id] += [Or(or_list)]

    def ensure_course_timeblock_paths(self):
        """
        Returns a list of z3 constraints that ensure there is an available
        course path for each student. (i.e. the courses they need have at least one
        configuration where none of them have Timeblock conflicts)
        """
        const_list = []
        self.course_index_list_cache = []
        for student_reqs in self.student_requirement_set:
            # print("adding timeblock_course z3 constraint for student {}".format(student_reqs.student_id))
            const_list += self.add_timeblock_constraints_for_student(student_reqs)

        return const_list

    def check_fact_utilization(self):
        """
        Looks at the number of needed classes v.s. teachers, classrooms, and timeblocks to
        see if the amount we have is close to the min required
        """
        teacher_utils = {}
        classroom_utils = {}

        for course_id, class_list in self.class_constraints.items():
            # make sure theres enough teachers for the number of courses
            teacher_ids = class_list[0].get_teacher_ids()
            timeblock_ids = class_list[0].get_timeblock_ids()
            classroom_ids = class_list[0].get_classroom_ids()

            timeblock_count = len(timeblock_ids)
            teacher_count = len(teacher_ids)
            classroom_count = len(classroom_ids)
            class_count = len(class_list)

            teacher_max = timeblock_count * teacher_count
            classroom_max = timeblock_count * classroom_count

            if class_count > teacher_max:
                msg = "No solution, Not enough teachers for course: {} {}, teachers={}, classes={}".format(
                    course_id, class_list[0].course_name, teacher_count, class_count)
                SchedUtil.log_note("error", "Scheduler", msg)
                raise SchedulerNoSolution("Not enough classrooms")  
            elif len(class_list) > classroom_max:
                msg = "No solution, Not enough classrooms for course: {} {}, classrooms={}, classes={}".format(
                    course_id, class_list[0].course_name, classroom_count, class_count)
                SchedUtil.log_note("error", "Scheduler", msg)
                raise SchedulerNoSolution("Not enough classrooms")  
            # else:
            #     print('\033[92m Course      {} {} \033[0m'.format(course_id, class_list[0].course_name))
            #     print('\033[92m class count {} \033[0m'.format(class_count))
            #     print('\033[92m teachers    {} \n\033[0m'.format(teacher_ids))

            for t_id in teacher_ids:
                if t_id not in teacher_utils:
                    teacher_utils[t_id] = 0.0
                teacher_utils[t_id] += 1/teacher_count * class_count

            for c_id in classroom_ids:
                if c_id not in classroom_utils:
                    classroom_utils[c_id] = 0.0
                classroom_utils[c_id] += 1/classroom_count * class_count




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

    

    # We setup some shortcuts to the accessors in the class constructor above just to make
    # coding easier and more readable
    def teacher(self, i):
        return SchClass.teacher(self.z3_classes[i])

    def room(self, i):
        return SchClass.room(self.z3_classes[i])

    def course(self, i):
        return SchClass.course(self.z3_classes[i])

    def time(self, i):
        return SchClass.time(self.z3_classes[i])

    def set_courses(self):
        """
        Returns a list of z3 constraints that make sure the scheduler includes the 
        courses we need as determined by calc_class_constraints (stored in self.class_constraints)
        """
        cons_list = []
        i = 0
        # loop through set courses and add constraints for each course
        # we'll first set the first level of constraints, then set 'If' conditions for the deeper levels
        for course_id, class_const_list in self.class_constraints.items():
            for class_const in class_const_list:
                class_const.z3_index = i
                cons_list += [ And(self.course(i) == course_id,
                                   Or([ self.teacher(i) == t_id for t_id in class_const.get_teacher_ids() ]),
                                   Or([ self.room(i) == r_id for r_id in class_const.get_classroom_ids() ]),
                                   Or([ self.time(i) == t_id for t_id in class_const.get_timeblock_ids() ])) ]
                
                # set the constraints from teacher to course, room, and time. 
                # This constraint reads: If the course is this one and the teacher is this one, then 
                # the rooms and times must be within the set of available rooms and times
                for teacher_constraint in class_const.get_teacher_constraints():
                    cons_list += [ If(And(self.course(i) == course_id, self.teacher(i) == teacher_constraint.teacher_id),
                                      And(Or([ self.room(i) == r_id for r_id in teacher_constraint.get_classroom_ids()]),
                                          Or([ self.time(i) == t_id for t_id in teacher_constraint.get_timeblock_ids()])),
                                      True) ]

                    # now do the same for rooms and times
                    for classroom_constraint in teacher_constraint.get_classroom_constraints():
                        cons_list += [ If(And(self.course(i) == course_id, 
                                              self.teacher(i) == teacher_constraint.teacher_id,
                                              self.room(i) == classroom_constraint.classroom_id),
                                          Or([ self.time(i) == t_id for t_id in classroom_constraint.get_timeblock_ids() ]),
                                          True) ] 
                i += 1

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


class ConstraintConflictException(Exception):
    pass


class StudentRequirements:
    def __init__(self, student_id, required_course_ids, optional_course_ids):
        self.student_id = student_id
        self.required_course_ids = required_course_ids
        self.optional_course_ids = optional_course_ids











