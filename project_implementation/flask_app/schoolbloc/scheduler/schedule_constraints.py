from z3 import *
from schoolbloc.scheduler.models import *
from schoolbloc.config import config

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
        self.course_time_constraints = [] # constraints generated from course-time collisions

        self.class_constraints = {} 
        self.student_requirement_set = [] # list of StudentRequirement objects

        self.prep_class_constraints()
        self.prep_z3_classes()
        self.prep_implied_constraints()
        self.prep_db_constraints()

    def get_constraints(self):
        """
        returns the current set of constraints
        """
        return self.db_constraints + self.course_time_constraints


    def prep_z3_classes(self):
        self.z3_classes = [Const("class_%s" % (i + 1), SchClass) for i in range(self.class_count)] 

    def prep_implied_constraints(self):
        self.db_constraints += self.set_courses()
        self.db_constraints += self.prevent_room_time_collision()
        self.db_constraints += self.prevent_teacher_time_collision() 

    def prep_db_constraints(self):
        self.db_constraints += self.constrain_course_rooms()
        self.db_constraints += self.constrain_room_time()
        self.db_constraints += self.constrain_course_time()
        self.db_constraints += self.constrain_teacher_time()
        self.db_constraints += self.constrain_course_teachers()

    def reset_constraints(self):
        """
        Re-calculates the implied constraints and the database constraints
        """
        self.db_constraints = []
        self.prep_z3_classes()
        self.prep_implied_constraints()
        self.prep_db_constraints()

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
            self.check_if_student_is_overscheduled(req_courses)
            # now go through the list and create courses when needed
            for course_id in req_courses:
                if course_id not in self.class_constraints:
                    new_class = ClassConstraint(course_id)
                    self.class_constraints[course_id] = [new_class]
                    self.class_count += 1
                
                elif self.class_constraints[course_id][0].student_count < ScheduleConstraints.max_student_count(course_id):
                    self.class_constraints[course_id][0].student_count += 1
                
                else:
                    new_class = ClassConstraint(course_id)
                    self.class_constraints[course_id].insert(0, new_class)
                    self.class_count += 1

    def check_if_student_is_overscheduled(self, required_courses):
        timeblock_count = Timeblock.query.count()
        if len(required_courses) > timeblock_count:
            msg = "Student {} course req ({}) is greater than time block count ({})".format(
                student.id, len(required_courses), timeblock_count)
            raise SchedulerNoSolution(msg)
            
    def gen_constraints_from_collisions(self, collisions):
        for col in collisions:
            msg = "{} collision on student {} course {}".format(
                col.collision_type, col.student.id, col.scheduled_class.course_id)
            print('\033[91m{}\033[0m'.format(msg))
            # now make a constraint to avoid the collision
            if col.collision_type == 'timeblock':
                # self.add_class_of_course(col.scheduled_class.course_id)
                # self.restrict_timeblocks(col.scheduled_class.course_id, col.scheduled_class.timeblock_id)
                self.add_timeblock_constraints_for_student(col.student)

            elif col.collision_type == 'full class':
                pass

    def add_class_for_course(self, course_id):
        class_const = ClassConstraint(course_id)
        class_const.timeblock_ids = self.calc_avail_timeblocks(course_id)
        class_const.teacher_ids = self.calc_avail_teachers(course_id)
        class_const.room_ids = self.calc_avail_rooms(course_id)
        
        self.class_constraints[course_id].append(class_const)
        self.class_count += 1
        print('\033[91m Added ClassConstraint: {}\033[0m'.format(class_const))

    def add_timeblock_constraints_for_student(self, student):
        """
        Go through the courses required by the student and add a constraint that 
        prevents timeblock collisions for any of the required courses
        """
        print('\033[93m adding course time constraint for student: {}\033[0m'.format(student.id))
        # build a 2 dimensional array representing the z3 indices of the 
        # required courses for the student. where the members if each each inner list 
        # represent the same course
        course_indexes = [ [ c.z3_index for c in self.class_constraints[course_id] ] 
                          for course_id in student.required_course_ids ]

        print('\033[93m course z3 index set:\n {}\033[0m'.format(course_indexes))

        # now generate all the possible course paths for the student
        path_list = ScheduleConstraints.gen_course_path_list(course_indexes)

        print('\033[93m all possible course paths:\n {}\033[0m'.format(path_list))

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

        self.course_time_constraints += [ Or(or_list) ]



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
                                   Or([ self.room(i) == r_id for r_id in class_const.room_ids]),
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
            if room.avail_start_time or room.avail_end_time:
                # figure out which time blocks can be assigned to the room
                avail_time_ids = self.calc_avail_time_ids(room.avail_start_time, room.avail_end_time)
                
                cons_list += [ If(self.room(i) == room.id, 
                                  Or([ self.time(i) == time_id for time_id in avail_time_ids ]),
                                  True)
                               for i in range(self.class_count) ]
            else:
                room_times = ClassroomsTimeblock.query.filter_by(classroom_id=room.id).all()
                if len(room_times) > 0:
                    # collect all the timeblocks mapped to this room
                    timeblock_ids = [ rt.timeblock_id for rt in room_times ]
                    cons_list += [ If(self.room(i) == room.id, 
                                      Or([ self.time(i) == time_id for time_id in timeblock_ids ]),
                                      True)
                                   for i in range(self.class_count)]
        return cons_list
    
    def constrain_teacher_time(self):
        """ 
        returns a list of z3 constrains that prevent a teacher from being scheduled beyond 
        his/her available start and end times 
        """

        cons_list = []
        for teacher in Teacher.query.all():
            if teacher.avail_start_time or teacher.avail_end_time:
                # figure out which time blocks can be assigned to the teacher
                avail_time_ids = self.calc_avail_time_ids(teacher.avail_start_time, teacher.avail_end_time)
                
                cons_list += [ If(self.teacher(i) == teacher.id, 
                                  Or([ self.time(i) == time_id for time_id in avail_time_ids ]),
                                  True)
                               for i in range(self.class_count) ]
            else:
                teacher_times = TeachersTimeblock.query.filter_by(teacher_id=teacher.id).all()
                if len(teacher_times) > 0:
                    # collect all the timeblocks mapped to this teacher
                    timeblock_ids = [ tt.timeblock_id for tt in teacher_times ]
                    cons_list += [ If(self.teacher(i) == teacher.id, 
                                      Or([ self.time(i) == time_id for time_id in timeblock_ids ]),
                                      True)
                                   for i in range(self.class_count)]

        return cons_list

    def constrain_course_time(self):
        """ 
        returns a list of z3 constrains that prevent a course from being scheduled beyond 
        its available start and end times 
        """

        cons_list = []
        for course in Teacher.query.all():
            if course.avail_start_time or course.avail_end_time:
                # figure out which time blocks can be assigned to the course
                avail_time_ids = self.calc_avail_time_ids(course.avail_start_time, course.avail_end_time)
                
                cons_list += [ If(self.course(i) == course.id, 
                                  Or([ self.time(i) == time_id for time_id in avail_time_ids ]),
                                  True)
                               for i in range(self.class_count) ]
            else:
                course_times = CoursesTimeblock.query.filter_by(course_id=course.id).all()
                if len(course_times) > 0:
                    # collect all the timeblocks mapped to this course
                    timeblock_ids = [ ct.timeblock_id for ct in course_times ]
                    cons_list += [ If(self.course(i) == course.id, 
                                      Or([ self.time(i) == time_id for time_id in timeblock_ids ]),
                                      True)
                                   for i in range(self.class_count)]

        return cons_list

class StudentRequirements:
    def __init__(self, student_id, required_course_ids, optional_course_ids):
        self.student_id = student_id
        self.required_course_ids = required_course_ids
        self.optional_course_ids = optional_course_ids


class ClassConstraint:
    def __init__(self, course_id):
        """
        Represents the constraints applied to a single class. These objects are generated by the 
        Scheduler and used to hold known constraints for a class (for example, it's course).
        """
        self.course_id = course_id
        self.z3_index = 0
        self.student_count = 0
        self.calc_avail_rooms()
        self.calc_avail_teachers()
        self.calc_avail_timeblocks()

    def __repr__(self):
        return "course_id: {}, room_ids: {}, teacher_ids: {}, timeblock_ids: {}".format(
            self.course_id, self.room_ids, self.teacher_ids, self.timeblock_ids)

    def calc_avail_rooms(self):
        """
        Takes a course_id and returns a list of room_ids available to the course based
        on constraints in the DB
        """
        # TODO: consider constraints and priorities
        self.room_ids = [ room.id for room in Classroom.query.all() ]

    def calc_avail_teachers(self):
        """
        Takes a course_id and returns a list of teacher_ids available to the course based
        on constraints in the DB
        """
        # TODO: consider constraints and priorities
        self.teacher_ids = [ teacher.id for teacher in Teacher.query.all() ]

    def calc_avail_timeblocks(self):
        """
        Takes a course_id and returns a list of timeblock_ids available to the course based
        on constraints in the DB
        """
        # TODO: consider constraints and priorities
        # return [ timeblock.id for timeblock in Timeblock.query.all() ]
        self.timeblock_ids = [ timeblock.id for timeblock in Timeblock.query.all() ]
