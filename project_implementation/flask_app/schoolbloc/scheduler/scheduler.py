from z3 import *
from schoolbloc.scheduler.models import *
from schoolbloc import db
from schoolbloc.config import config

DEFAULT_MAX_CLASS_SIZE = 30

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





class SchedulerNoSoltuion(Exception):
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
    

    def max_class_size(self, course_id=None, classroom_id=None):
        """ 
        Determines the maximum student count based on the given course and/or classroom.
        The max count is the lesser of the two if both course and classroom are given.
        """
        
        course = Course.query.get(course_id)
        classroom = Classroom.query.get(classroom_id)

        if course and course.max_student_count:
            if classroom and classroom.max_student_count:
                return min(course.max_student_count, classroom.max_student_count)
            else:
                return course.max_student_count
        else:
            if classroom and classroom.max_student_count:
                return classroom.max_student_count
        return DEFAULT_MAX_CLASS_SIZE

    # ensures the teacher, room, and course ids are valid
    def ensure_valid_ids(self):

        teacher_ids = [t.id for t in Teacher.query.all()]
        room_ids = [r.id for r in Classroom.query.all()]
        course_ids = [c.id for c in Course.query.all()]
        student_ids = [s.id for s in Student.query.all()]

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

    def ensure_valid_class_durations(self):
        """ returns a list of z3 constraints to make sure each class is either its
            specified duration or the default duration """
        cons_list = []
        for c in Course.query.all():
            if c.duration:
                cons_list += [ If(self.course(i) == c.id, 
                                  TimeBlock.end(self.time(i)) - TimeBlock.start(self.time(i)) == c.duration,
                                  True) for i in range(self.class_count) ]
            else:
                cons_list += [ If(self.course(i) == c.id, 
                                  TimeBlock.end(self.time(i)) - TimeBlock.start(self.time(i)) == self.class_duration,
                                  True) for i in range(self.class_count) ] 
        return cons_list

    def ensure_valid_class_start_times(self):
        """ returns a list of z3 constraints to make sure each class falls into a valid start time """
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

        return [ Or([TimeBlock.start(self.time(i)) == s for s in start_times]) for i in range(self.class_count) ]

    def ensure_lunch_period(self):
        """ returns a list of z3 constraints making sure no class falls within the lunch period """
        return [ Or(TimeBlock.start(self.time(i)) >= self.lunch_end, TimeBlock.end(self.time(i)) <= self.lunch_start) 
                 for i in range(self.class_count) ]

    # prevent a room from being assigned to two classes that occur at the same time
    def prevent_room_time_collision(self):
        return [ If(And(i != j, self.room(i) == self.room(j)),
                     Not( Or( And( TimeBlock.start(self.time(i)) <= TimeBlock.start(self.time(j)), 
                                   TimeBlock.end(self.time(i)) >= TimeBlock.end(self.time(j)) ),
                              And( TimeBlock.start(self.time(i)) <= TimeBlock.start(self.time(j)), 
                                   TimeBlock.end(self.time(i)) >= TimeBlock.start(self.time(j)) ),
                              And( TimeBlock.start(self.time(i)) <= TimeBlock.end(self.time(j)),
                                   TimeBlock.end(self.time(i)) >= TimeBlock.end(self.time(j)) ))),  # then
                     True)  # else
                  for i in range(self.class_count) for j in range(self.class_count) ]

    # prevent a teacher from being assigned to two classes that occur at the same time
    def prevent_teacher_time_collision(self):
        return [ If(And(i != j, self.teacher(i) == self.teacher(j)), 
                    Not(self.time(i) == self.time(j)),
                    True)
                for i in range(self.class_count) for j in range(self.class_count)]

    # prevent a student from being assigned to two classes that occur at the same time
    def prevent_student_time_collision(self):
        x2 = Int(self.next_int_name())   
        x3 = Int(self.next_int_name())
        return [If(And(i != j, self.time(i) == self.time(j)),
                     ForAll([x2, x3], self.students(i)[x2] != self.students(j)[x3]), True)
                  for i in range(self.class_count) for j in range(self.class_count)]

    # prevent the same student from being assigned into the class twice
    def prevent_duplicate_student(self):
        x = Int(self.next_int_name())
        y = Int(self.next_int_name())
        return [If(x != y, self.students(i)[x] != self.students(i)[y], True) for i in
                  range(self.class_count)]

    def constrain_course_rooms(self):
        """ returns a list of z3 constraints for relationships between courses and rooms. """
        
        cons_models = ClassroomsCourse.query.all()
        cons_list = []
        # we need to construct a big 'OR' clause for each course that has 
        # all the available rooms. We'll restructure the data to make this easier
        mod_map = {}
        for mod in cons_models:
            if mod.course_id not in mod_map:
                mod_map[mod.course_id] = [mod.classroom_id]
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

    # def constrain_teacher_time(self):
    #     """ returns a list of z3 constraints for each teacher's available time """

    #     cons_list = []
    #     # if the teacher's start and/or end properties are set than
    #     # add constraints, else let the defaults kick in
    #     for teach in Teacher.query.all():

    #         if teach.start_time:
    #             cons_list += [ If( self.teacher(i) == teach.id, 
    #                                 TimeBlock.start(self.time(i)) >= teach.start_time, 
    #                                 True ) 
    #                             for i in range(self.class_count) for j in range(self.class_count) ]
    #         if teach.end_time:
    #             cons_list += [ If( self.teacher(i) == teach.id, 
    #                                 TimeBlock.end(self.time(i)) >= teach.end_time, 
    #                                 True ) 
    #                             for i in range(self.class_count) for j in range(self.class_count) ]

    #     return cons_list

    def constrain_course_size(self):
        """ returns a list of z3 constraints for min and max student count on each course """

        # The size if the student lists are abstract. Here we basically make sure the list returns
        # a distinct value for indices up to the min class size, then we make sure anything over 
        # the max size is NOT distinct. Then when figuring out what students are assigned to this class
        # we pull students until we start seing duplicates
        # return [ Distinct([ self.students(i)[j] for j in range(self.max_class_size(self.course(i), self.room(i)))]) 
        #         for i in range(self.class_count)]

        cons_list = []
        course_ids = [ c.id for c in Course.query.all() ]
        room_ids = [ r.id for r in Classroom.query.all() ]
        for course_id in course_ids:
            for room_id in room_ids:
                cons_list += [ If( And(self.course(i) == course_id, self.room(i) == room_id ),
                                    Distinct([ self.students(i)[j] for j in range(self.max_class_size(course_id, room_id))]),
                                    True)
                                for i in range(self.class_count)]
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
        return cons_list

    def constrain_student_req_courses(self):
        """ returns a list of z3 constraints for courses a student must take """

        cons_list = []
        # constraints of students to courses can come as direct relationships between students and 
        # courses, or by the student being a member of a student group that has a constraint 
        # relationship with the course. 
        for cs in CoursesStudent.query.all():
            x = Int(self.next_int_name())
            cons_list += [ Or([ And(self.course(i) == cs.course_id, self.students(i)[x] == cs.student_id) 
                           for i in range(self.class_count) ]) ]

        for c_grp in CoursesStudentGroup.query.all():
            for stud in c_grp.student_group.students:
                x = Int(self.next_int_name())
                cons_list += [ Or([ And(self.course(i) == c_grp.course_id, self.students(i)[x] == stud.id) 
                               for i in range(self.class_count) ]) ]

        return cons_list


    def make_schedule(self):
        
        constraints = []
        # all classes must be distinct
        # constraints = [Distinct([classes[i] for i in range(class_count)])]

        # Now we'll start adding constraints. The first set are implied constraints like
        # a teacher can't be in two places at one time.
        constraints += self.ensure_valid_ids()
        constraints += self.ensure_valid_class_durations()
        constraints += self.ensure_valid_class_start_times()
        constraints += self.ensure_lunch_period()
        constraints += self.prevent_room_time_collision()
        constraints += self.prevent_teacher_time_collision()
        constraints += self.prevent_student_time_collision()
        constraints += self.prevent_duplicate_student()

        # next, include the user provided constraints
        constraints += self.constrain_course_rooms()
        # constraints += self.constrain_teacher_time()
        constraints += self.constrain_course_size()
        constraints += self.constrain_student_req_courses()


      

        # Finally, ask the solver to give us a schedule and then parse the results
        s = Solver()
        s.add(constraints)
        if s.check() != sat:
            raise SchedulerNoSoltuion()
        else:
            m = s.model()
            
            # first, make the schedule object and then assign the classes to it
            new_schedule = Schedule('sample schedule')
            db.session.add(new_schedule)
            db.session.commit() # need to commit here because we need the schedule id

            for i in range(self.class_count):
                c = ScheduledClass(new_schedule.id,
                                   int(str(m.evaluate(self.course(i)))), 
                                   int(str(m.evaluate(self.room(i)))),
                                   int(str(m.evaluate(self.teacher(i)))),
                                   int(str(m.evaluate(TimeBlock.start(self.time(i))))),
                                   int(str(m.evaluate(TimeBlock.end(self.time(i))))))
                db.session.add(c)
                db.session.commit() # need to commit here because we need the ScheduledClass Id to add students

                # # now add the students to the new class. the z3 arrays are undefined length (they will return values
                # # for any index we give them.) we'll pull values until the max class size after that the values should
                # # voilate the unique constraint.
                for j in range(self.max_class_size(int(str(m.evaluate(self.course(i)))), int(str(m.evaluate(self.room(i)))))):
                    class_student = ScheduledClassesStudent(student_id=int(str(m.evaluate(self.students(i)[j]))), scheduled_class_id=c.id)
                    db.session.add(class_student) 
                db.session.commit()
        


