# from schoolbloc.scheduler.scheduler import SchedulerNoSolution
from z3 import *
from schoolbloc.scheduler.models import *
from schoolbloc.config import config
import math
import time

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

    def prep_z3_classes(self):
        self.z3_classes = [Const("class_%s" % (i + 1), SchClass) for i in range(self.class_count)] 

    def prep_implied_constraints(self):
        self.db_constraints += self.set_courses()
        print('\033[92m class count: {} \033[0m'.format( self.class_count))
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
        print("reset constraints ( {} min )".format(round((time.time() - start_time)/60)))

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
                max_stud_count = int(ScheduleConstraints.max_student_count(course_id) * .9)
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
            msg = "Student {} course req ({}) is greater than time block count ({})".format(
                student.id, len(required_courses), timeblock_count)
            raise SchedulerNoSolution(msg)
        elif len(required_courses) < timeblock_count:
            print("\033[91m Warning: Student {} course requirements are less than full time \033[0m".format(student.id))
            
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
        print('\033[91m Added Class for course: {} {}\033[0m'.format(course.id, course.name))
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
            teacher_ids = class_list[0].teacher_ids
            timeblock_ids = class_list[0].timeblock_ids
            classroom_ids = class_list[0].classroom_ids

            timeblock_count = len(timeblock_ids)
            teacher_count = len(teacher_ids)
            classroom_count = len(classroom_ids)
            class_count = len(class_list)

            teacher_max = timeblock_count * teacher_count
            classroom_max = timeblock_count * classroom_count

            if class_count > teacher_max:
                print("\033[91m No solution, Not enough teachers for course: {} {}, teachers={}, classes={}\033[0m".format(
                    course_id, class_list[0].course_name, teacher_count, class_count))
                raise SchedulerNoSolution("Not enough classrooms")  
            elif len(class_list) > classroom_max:
                print("\033[91m No solution, Not enough classrooms for course: {} {}, classrooms={}, classes={}\033[0m".format(
                    course_id, class_list[0].course_name, classroom_count, class_count))
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

        #print('\033[92m \n Teacher Utilization (for {} timeblocks ) \n {} \n\033[0m'.format(timeblock_count, teacher_utils))
        #print('\033[92m \n Classroom Utilization (for {} timeblocks ) \n {} \n\033[0m'.format(timeblock_count, classroom_utils))
        

    # def prep_class_constraints(self):
    #     """
    #     Calculates the courses needed from the required corses for each student.
    #     In the case of a Subject requirement, without a course requirement for the 
    #     Subject, a course is arbritrarily assigned. The calculated course needs are stored 
    #     in ClassConstraint objects

    #     Also, this method creates a list of SchedulerStudent objects with their required
    #     course ids. It also detects when
    #     a student is assigned to more courses than there are time_blocks in the schedule
    #     """
    #     self.class_constraints = {}
    #     self.sched_students = []
    #     course_student_counts = {}

    #     # we go through each student and make a list of their required courses. We also
    #     # count the number of students for each course. 
    #     for student in Student.query.all():
    #         req_courses = self.calc_student_courses(student.id)
    #         sched_student = ScheduleStudent(student.id, len(self.time_blocks), req_courses, [])
    #         self.sched_students.append(sched_student)

    #         # detect if the student is over scheduled
    #         if len(req_courses) > len(self.time_blocks):
    #             msg = "Student {} course req ({}) is greater than time block count ({})".format(
    #                 student.id, len(req_courses), len(self.time_blocks))
    #             raise SchedulerNoSolution(msg)
    #         else:
    #             for course_id in req_courses:
    #                 if course_id not in course_student_counts:
    #                     course_student_counts[course_id] = 0
    #                 course_student_counts[course_id] += 1

    #     # now we know how many students are assigned to each course. we'll go through each 
    #     # and determine the total course count from the max student count of each course
    #     self.class_count = 0
    #     for course_id, student_count in course_student_counts.items():
    #         max_stud_count = self.max_class_size(course_id)
    #         course_count = int(student_count / max_stud_count)
    #         # if it didn't divide cleanly, then add 1 more class for that course
    #         if student_count % max_stud_count != 0:
    #             course_count += 1
    #         self.class_count += course_count
    #         # now make a ClassConstraint object for each course
    #         if course_id not in self.class_constraints:
    #             self.class_constraints[course_id] = []
    #         for i in range(course_count):
    #             class_cons = ClassConstraint(course_id)
    #             class_cons.room_ids = self.calc_avail_rooms(course_id)
    #             class_cons.teacher_ids = self.calc_avail_teachers(course_id)
    #             class_cons.timeblock_ids = self.calc_avail_timeblocks(course_id)

    #             self.class_constraints[course_id].append(class_cons)


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
        for course_id, class_const_list in self.class_constraints.items():
            for class_const in class_const_list:
                class_const.z3_index = i
                cons_list += [ And(self.course(i) == course_id,
                                   Or([ self.teacher(i) == t_id for t_id in class_const.teacher_ids ]),
                                   Or([ self.room(i) == r_id for r_id in class_const.classroom_ids]),
                                   Or([ self.time(i) == t_id for t_id in class_const.timeblock_ids ])) ]
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

    # def constrain_course_rooms(self):
    #     """ returns a list of z3 constraints for relationships between courses and rooms. """
        
    #     cons_models = ClassroomsCourse.query.all()
    #     cons_list = []
    #     # we need to construct a big 'OR' clause for each course that has 
    #     # all the available rooms. We'll restructure the data to make this easier
    #     mod_map = {}
    #     for mod in cons_models:
    #         if mod.course_id not in mod_map:
    #             mod_map[mod.course_id] = [mod.classroom_id, 0]
    #         else:
    #             mod_map[mod.course_id].append(mod.classroom_id)

    #     # now we can loop through the map's keys and add the constraints
    #     for course_id in mod_map.keys():

    #         # the rooms aren't grouped in the DB so we look through all the models and 
    #         # construct a list of rooms available to this course.
    #         cons_list += [ If( self.course(i) == course_id, 
    #                            Or([ self.room(i) == room_id for room_id in mod_map[course_id] ]), 
    #                            True )  
    #                         for i in range(self.class_count) for j in range(self.class_count) ]
    #     return cons_list

    # def constrain_course_teachers(self):
    #     cons_list = []
        
    #     # build a list of courses each teacher can teach
    #     ct_map = {}
    #     for ct in CoursesTeacher.query.all():
    #         if ct.course_id in ct_map:
    #             ct_map[ct.course_id].append(ct.teacher_id)
    #         else:
    #             ct_map[ct.course_id] = [ct.teacher_id]

    #     # now make the constraint
    #     if len(ct_map) == 0:
    #         return cons_list

    #     for c_id, t_id_list in ct_map.items():
    #         cons_list += [ If(self.course(i) == c_id,
    #                           Or([ self.teacher(i) == t_id for t_id in t_id_list]), 
    #                           True) 
    #                        for i in range(self.class_count) ]
    #     return cons_list

    #def calc_avail_time_ids(self, start_time=None, end_time=None):
    #    times = []
    #    for i in range(self.time_blocks):
    #        time_block = self.time_blocks[i]
    #        if start_time and end_time:
    #            if start_time >= time_block.start and end_time <= time_block.end:
    #                times.append(i)
    #        elif start_time:
    #            if start_time >= time_block.start:
    #                times.append(i)
    #        elif end_time:
    #            if end_time <= time_block.end:
    #                times.append(i)
    #        else:
    #            times.append(i)


    #def constrain_room_time(self):
    #    """ 
    #    returns a list of z3 constrains that prevent a room from being scheduled beyond 
    #    its available start and end times 
    #    """
#
#        cons_list = []
#        for room in Classroom.query.all():
#            room_times = ClassroomsTimeblock.query.filter_by(classroom_id=room.id).all()
#            if len(room_times) > 0:
#                # collect all the timeblocks mapped to this room
#                timeblock_ids = [ rt.timeblock_id for rt in room_times ]
#                cons_list += [ If(self.room(i) == room.id, 
#                                  Or([ self.time(i) == time_id for time_id in timeblock_ids ]),
#                                  True)
#                               for i in range(self.class_count)]
#        return cons_list
    
#    def constrain_teacher_time(self):
#        """ 
#        returns a list of z3 constrains that prevent a teacher from being scheduled beyond 
#        his/her available start and end times 
#        """
#
#        cons_list = []
#        for teacher in Teacher.query.all():
#            if teacher.avail_start_time or teacher.avail_end_time:
#                # figure out which time blocks can be assigned to the teacher
#                avail_time_ids = self.calc_avail_time_ids(teacher.avail_start_time, teacher.avail_end_time)
#                
#                cons_list += [ If(self.teacher(i) == teacher.id, 
#                                  Or([ self.time(i) == time_id for time_id in avail_time_ids ]),
#                                  True)
#                               for i in range(self.class_count) ]
#            else:
#                teacher_times = TeachersTimeblock.query.filter_by(teacher_id=teacher.id).all()
#                if len(teacher_times) > 0:
#                    # collect all the timeblocks mapped to this teacher
#                    timeblock_ids = [ tt.timeblock_id for tt in teacher_times ]
#                    cons_list += [ If(self.teacher(i) == teacher.id, 
#                                      Or([ self.time(i) == time_id for time_id in timeblock_ids ]),
#                                      True)
#                                   for i in range(self.class_count)]
#
#        return cons_list

    # def constrain_course_time(self):
    #     """ 
    #     returns a list of z3 constrains that prevent a course from being scheduled beyond 
    #     its available start and end times 
    #     """

    #     cons_list = []
    #     for course in Teacher.query.all():
    #         course_times = CoursesTimeblock.query.filter_by(course_id=course.id).all()
    #         if len(course_times) > 0:
    #             # collect all the timeblocks mapped to this course
    #             timeblock_ids = [ ct.timeblock_id for ct in course_times ]
    #             cons_list += [ If(self.course(i) == course.id, 
    #                               Or([ self.time(i) == time_id for time_id in timeblock_ids ]),
    #                               True)
    #                            for i in range(self.class_count)]

    #     return cons_list

class StudentRequirements:
    def __init__(self, student_id, required_course_ids, optional_course_ids):
        self.student_id = student_id
        self.required_course_ids = required_course_ids
        self.optional_course_ids = optional_course_ids


class TeacherConstraint:
    def __init__(self, teacher_id):
        self.teacher_id = teacher_id
        self.timeblock_constraints = []
        self.classroom_constraints = []
        self.subject_ids = []

        # self.calc_subject_ids()
        # self.gen_classroom_constraints()
        # self.gen_timeblock_constraints()

    def calc_subject_ids(self):
        ts_list = TeachersSubject.query.filter_by(teacher_id=self.teacher_id).all()
        self.subject_ids = [ cs.subject_id for cs in ts_list ]

    def calc_classroom_constraints(self):
        ct_low_list = ClassroomsTeacher.query.filter_by(priority='low', teacher_id=self.teacher_id).all()

        cs_low_list = []
        for subject_id in self.subject_ids:
            cs_low_list += ClassroomsSubject.query.filter_by(priority='low', subject_id=subject_id).all()

        if len(ct_low_list) > 0 or len(cs_low_list) > 0:
            self.classroom_constraints = [ ClassroomConstraint(cc.classroom_id) 
                                           for cc in ct_low_list ]
            self.classroom_constraints += [ ClassroomConstraint(cs.classroom_id) 
                                            for cs in cs_low_list ]
        else:
            self.classroom_constraints = [ c.id for c in Classroom.query.all() ]

    def calc_timeblock_constraints(self):
        tt_low_list = TeachersTimeblock.query.filter_by(priority='low', teacher_id=self.teacher_id).all()

        st_low_list = []
        for subject_id in self.subject_ids:
            st_low_list += SubjectsTimeblock.query.filter_by(priority='low', subject_id=subject_id).all()

        if len(tt_low_list) > 0 or len(st_low_list) > 0:
            self.timeblock_constraints = [ TimeblockConstraint(ct.timeblock_id) 
                                            for ct in tt_low_list ]
            self.timeblock_constraints += [ TimeblockConstraint(st.timeblock_id)
                                            for st in st_low_list ]
        else:
            self.timeblock_constraints = [ t.id for t in Timeblock.query.all() ]


class ClassroomConstraint:
    def __init__(self, classroom_id):
        self.classroom_id = classroom_id
        self.timeblock_constraints = []
        self.subject_ids = []
        # self.calc_subject_ids()
        # self.calc_timeblock_constraints()

    def calc_subject_ids(self):
        ts_list = TeachersSubject.query.filter_by(teacher_id=self.teacher_id).all()
        self.subject_ids = [ cs.subject_id for cs in ts_list ] 

    def calc_timeblock_constraints(self):
        tt_low_list = TeachersTimeblock.query.filter_by(priority='low', teacher_id=self.teacher_id).all()

        st_low_list = []
        for subject_id in self.subject_ids:
            st_low_list += SubjectsTimeblock.query.filter_by(priority='low', subject_id=subject_id).all()

        if len(tt_low_list) > 0 or len(st_low_list) > 0:
            self.timeblock_constraints = [ TimeblockConstraint(ct.timeblock_id) 
                                            for ct in tt_low_list ]
            self.timeblock_constraints += [ TimeblockConstraint(st.timeblock_id)
                                            for st in st_low_list ]
        else:
            self.timeblock_constraints = [ t.id for t in Timeblock.query.all() ]

class TimeblockConstraint:
    def __init__(self, timeblock_id):
        self.timeblock_id = timeblock_id


class ClassConstraint:
    def __init__(self, course_id, course_name):
        """
        Represents the constraints applied to a single class. These objects are generated by the 
        Scheduler and used to hold known constraints for a class (for example, it's course).
        """
        self.course_id = course_id
        self.course_name = course_name
        self.z3_index = 0
        self.student_count = 0

        self.teacher_constraints = []
        self.classroom_constraints = []
        self.timeblock_constraints = []
        self.subject_ids = []

        # now apply the constraints to this class
        self.calc_subject_ids()
        self.calc_teacher_constraints()
        self.calc_classroom_constraints()
        self.calc_timeblock_constraints()
        self.apply_constraints()


    def __repr__(self):
        return "course_id: {}, room_ids: {}, teacher_ids: {}, timeblock_ids: {}".format(
            self.course_id, self.room_ids, self.teacher_ids, self.timeblock_ids)

    def get_teacher_ids(self):
        """
        Returns a list of teacher ids that can be used for this class
        """
        return [ t.teacher_id for t in self.teacher_constraints ]

    def get_classroom_ids(self):
        """
        Returns a list of classroom ids that can be used for this class
        """

    def get_timeblock_ids(self):
        """
        Returns a list of timeblock its that can be used for this class
        """


    # we'll start with the full set of classrooms, teachers, and timeblocks available to this course
    # then apply the constraints to narrow down the lists

    def calc_subject_ids(self):
        course_subject_list = CoursesSubject.query.filter_by(course_id=self.course_id).all()
        self.subject_ids = [ cs.subject_id for cs in course_subject_list ]
    
    def calc_teacher_constraints(self):
        ct_low_list = CoursesTeacher.query.filter_by(priority='low', course_id=self.course_id).all()

        # also include teachers ids from the subjects that include this course
        st_low_list = []
        for subject_id in self.subject_ids:
            st_low_list += TeachersSubject.query.filter_by(priority='low', subject_id=subject_id).all()


        if len(ct_low_list) > 0 or len(st_low_list) > 0:
            self.teacher_constraints = [ TeacherConstraint(ct.teacher_id) for ct in ct_low_list ]
            self.teacher_constraints += [ TeacherConstraint(st.teacher_id) for st in st_low_list ]
        else:
            self.teacher_constraints += [ TeacherConstraint(t.id) for t in Teacher.query.all() ]

        self.teacher_ids = [ t.teacher_id for t in self.teacher_constraints ]

    def calc_classroom_constraints(self):
        cc_low_list = ClassroomsCourse.query.filter_by(priority='low', course_id=self.course_id).all()

        # also include classroom ids from the subjects that include this course
        cs_low_list = []
        for subject_id in self.subject_ids:
            cs_low_list += ClassroomsSubject.query.filter_by(priority='low', subject_id=subject_id).all()

        if len(cc_low_list) > 0 or len(cs_low_list) > 0:
            self.classroom_constraints = [ ClassroomConstraint(cc.classroom_id) 
                                           for cc in cc_low_list ]
            self.classroom_constraints += [ ClassroomConstraint(cs.classroom_id) 
                                            for cs in cs_low_list ]
        else:
            self.classroom_constraints = [ ClassroomConstraint(c.id) for c in Classroom.query.all() ]

        self.classroom_ids = [ t.classroom_id for t in self.classroom_constraints ]



    def calc_timeblock_constraints(self):
        ct_low_list = CoursesTimeblock.query.filter_by(priority='low', course_id=self.course_id).all()

        # also include timeblocks ids from the subjects that include this course
        st_low_list = []
        for subject_id in self.subject_ids:
            st_low_list += SubjectsTimeblock.query.filter_by(priority='low', subject_id=subject_id).all()

        if len(ct_low_list) > 0 or len(st_low_list) > 0:
            self.timeblock_constraints = [ TimeblockConstraint(ct.timeblock_id) 
                                            for ct in ct_low_list ]
            self.timeblock_constraints += [ TimeblockConstraint(st.timeblock_id)
                                            for st in st_low_list ]
        else:
            self.timeblock_constraints = [ TimeblockConstraint(t.id) for t in Timeblock.query.all() ]

        self.timeblock_ids = [ t.timeblock_id for t in self.timeblock_constraints ]


    # def calc_room_teacher_time_constraints(self):
    #     self.apply_course_teacher()
    #     self.apply_classroom_course()
    #     self.apply_course_timeblock()

    def apply_constraints(self):
        # go through the other constraint types and apply them, round-robin style until no changes are made
        change_count = 0
        while True:
            change_count += self.apply_classroom_teacher()
            change_count += self.apply_teacher_timeblock()
            change_count += self.apply_classroom_timeblock()
            
            # make sure we didn't make our lists empty
            self.check_id_lists()

            if change_count == 0:
                return
            else:
                change_count = 0

    def check_id_lists(self):
        if len(self.teacher_ids) <= 0:
            print("\033[91m No solution, course {} {} has 0 available teachers".format(
                    self.course_id, self.course_name))
            raise SchedulerNoSolution("0 teachers for course {} {}".format(self.course_id, self.course_name))  

        elif len(self.classroom_ids) <= 0:
            print("\033[91m No solution, course {} {} has 0 available classrooms".format(
                    self.course_id, self.course_name))
            raise SchedulerNoSolution("0 classrooms for course {} {}".format(self.course_id, self.course_name))  

        elif len(self.timeblock_ids) <= 0:
            print("\033[91m No solution, course {} {} has 0 available timeblocks".format(
                    self.course_id, self.course_name))
            raise SchedulerNoSolution("0 timeblocks for course {} {}".format(self.course_id, self.course_name))  
    
    


    def apply_classroom_teacher(self):
        """
        Narrow the field of teachers and classrooms based on ClassroomsTeacher constraints
        """
        # make the sets of classrooms that are available to our set of teachers. 
        # But, if any teacher has 0 ClassroomsTeacher constraints, then the full set of rooms
        # is available so we can't narrow our classroom list down
        count = 0
        all_classroom_ids = []
        for teacher_id in self.teacher_ids:
            low_list = ClassroomsTeacher.query.filter_by(priority='low', teacher_id=teacher_id).all()
            # if there are no constraints, we assume all are available so we can't narrow the list down
            if len(low_list) == 0:
                all_classroom_ids = []
                break
            else:
                all_classroom_ids += [ c.classroom_id for c in low_list ]

        # then remove any of our classrooms that are not present in any of the sets
        if len(all_classroom_ids) > 0:
            for classroom_id in self.classroom_ids:
                if classroom_id not in all_classroom_ids:
                    count += 1
                    self.classroom_ids.remove(classroom_id)

        # and do the same from the classroom perspective
        all_teacher_ids = []
        for classroom_id in self.classroom_ids:
            low_list = ClassroomsTeacher.query.filter_by(priority='low', classroom_id=classroom_id).all()
            # if there are no constraints, we assume all are available so we can't narrow the list down
            if len(low_list) == 0:
                all_teacher_ids = []
                break
            else:
                all_teacher_ids += [ ct.teacher_id for ct in low_list ]

        # then remove any of our teachers that are not present in any of the sets
        if len(all_teacher_ids) > 0:
            for teacher_id in self.teacher_ids:
                if teacher_id not in all_teacher_ids:
                    count += 1 
                    self.teacher_ids.remove(teacher_id)

        return count

    def apply_teacher_timeblock(self):
        # make the sets of timeblocks that are available to our set of teachers. 
        # But, if any teacher has 0 TeacherTimeblock constraints, then the full set of timeblocks
        # is available so we can't narrow our timeblock list down
        count = 0
        all_timeblock_ids = []
        for teacher_id in self.teacher_ids:
            low_list = TeachersTimeblock.query.filter_by(priority='low', teacher_id=teacher_id).all()
            if len(low_list) == 0:
                all_timeblock_ids = []
                break
            else:
                all_timeblock_ids += [ tt.timeblock_id for tt in low_list ]
        
        if len(all_timeblock_ids) > 0:
            for timeblock_id in self.timeblock_ids:
                if timeblock_id not in all_timeblock_ids:
                    count += 1
                    self.timeblock_ids.remove(timeblock_id)

        # and do the same from the timeblock perspective
        all_teacher_ids = []
        for timeblock_id in self.timeblock_ids:
            low_list = TeachersTimeblock.query.filter_by(priority='low', timeblock_id=timeblock_id).all()
            # if there are no constraints, we assume all are available so we can't narrow the list down
            if len(low_list) == 0:
                all_teacher_ids = []
                break
            else:
                all_teacher_ids += [ tt.teacher_id for tt in low_list ]

        # then remove any of our teachers that are not present in any of the sets
        if len(all_teacher_ids) > 0:
            for teacher_id in self.teacher_ids:
                if teacher_id not in all_teacher_ids:
                    count += 1 
                    self.teacher_ids.remove(teacher_id)

        return count

    def apply_classroom_timeblock(self):
        # make the sets of classrooms that are available to our set of timeblocks. 
        # But, if any timeblock has 0 ClassroomsTimeblock constraints, then the full set of rooms
        # is available so we can't narrow our classroom list down
        count = 0
        all_classroom_ids = []
        for timeblock_id in self.timeblock_ids:
            low_list = ClassroomsTimeblock.query.filter_by(priority='low', timeblock_id=timeblock_id).all()
            # if there are no constraints, we assume all are available so we can't narrow the list down
            if len(low_list) == 0:
                all_classroom_ids = []
                break
            else:
                all_classroom_ids += [ ct.classroom_id for ct in low_list ]

        # then remove any of our classrooms that are not present in any of the sets
        if len(all_classroom_ids) > 0:
            for classroom_id in self.classroom_ids:
                if classroom_id not in all_classroom_ids:
                    count += 1
                    self.classroom_ids.remove(classroom_id)

        # and do the same from the classroom perspective
        all_timeblock_ids = []
        for classroom_id in self.classroom_ids:
            low_list = ClassroomsTimeblock.query.filter_by(priority='low', classroom_id=classroom_id).all()
            # if there are no constraints, we assume all are available so we can't narrow the list down
            if len(low_list) == 0:
                all_timeblock_ids = []
                break
            else:
                all_timeblock_ids += [ ct.timeblock_id for ct in low_list ]

        # then remove any of our timeblocks that are not present in any of the sets
        if len(all_timeblock_ids) > 0:
            for timeblock_id in self.timeblock_ids:
                if timeblock_id not in all_timeblock_ids:
                    count += 1
                    self.timeblock_ids.remove(timeblock_id)

        return count





    # def apply_teacher_subject(self):
    #     # add the constraints from the TeachersSubject constraints
    #     for course_subject in CoursesSubject.query.filter_by(course_id=self.course_id).all():
    #         self.teacher_mand_const += [ ts.teacher_id for ts in TeachersSubject.query.filter_by(priority='mandatory', subject_id=course_subject.subject_id).all() ]
    #         self.teacher_high_const += [ ts.teacher_id for ts in TeachersSubject.query.filter_by(priority='high', subject_id=course_subject.subject_id).all() ]
    #         self.teacher_low_const += [ ts.teacher_id for ts in TeachersSubject.query.filter_by(priority='low', subject_id=course_subject.subject_id).all() ]

    # def calc_avail_rooms(self):
    #     # pull the classrooms_course constraints
    #     self.classroom_mand_const = ClassroomsCourse.query.filter_by(priority='mandatory', course_id=self.course_id).all()
    #     self.classroom_high_const = ClassroomsCourse.query.filter_by(priority='high', course_id=self.course_id).all()
    #     self.classroom_low_const = ClassroomsCourse.query.filter_by(priority='low', course_id=self.course_id).all()

    #     # now apply the ClassroomsTeacher, ClassroomsTimeblock, ClassroomsSubject, 

    #     # now define the current set of classrooms for this course. 
    #     if len(self.classroom_mand_const) > 0:
    #         self.classroom_ids = [ room.id for room in self.classroom_mand_const ]
    #     elif len(self.classroom_high_const) > 0:
    #         self.classroom_ids = [ room.id for room in self.classroom_high_const ]
    #     elif len(self.classroom_low_const) > 0:
    #         self.classroom_ids = [ room.id for room in self.classroom_low_const ]

    # def calc_avail_teachers(self):
        



#    def calc_avail_timeblocks(self):
#        """
#        Takes a course_id and returns a list of timeblock_ids available to the course based
#        on constraints in the DB
#        """
#        # pull the classrooms_course constraints
#        self.timeblock_mand_const = CoursesTimeblock.query.filter_by(priority='mandatory', course_id=self.course_id).all()
#        self.timeblock_high_const = CoursesTimeblock.query.filter_by(priority='high', course_id=self.course_id).all()
#        self.timeblock_low_const = CoursesTimeblock.query.filter_by(priority='low', course_id=self.course_id).all()

#        # now define the current set of timeblocks for this course. 
#        if len(self.timeblock_mand_const) > 0:
#            self.timeblock_ids = [ timeblock.id for timeblock in self.timeblock_mand_const ]
#        elif len(self.timeblock_high_const) > 0:
#            self.timeblock_ids = [ timeblock.id for timeblock in self.timeblock_high_const ]
#        elif len(self.timeblock_low_const) > 0:
#            self.timeblock_ids = [ timeblock.id for timeblock in self.timeblock_low_const ]
