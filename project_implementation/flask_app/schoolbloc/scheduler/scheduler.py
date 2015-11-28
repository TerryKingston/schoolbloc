from z3 import *
from schoolbloc.users.models import User
from schoolbloc.teachers.models import Teacher
from schoolbloc.classrooms.models import Classroom
from schoolbloc.students.models import Student
from schoolbloc.courses.models import Course
from schoolbloc.scheduled_classes.models import ScheduledClass


class SchedulerNoSoltuion(Exception):
    pass

# default config values. Should pull this stuff from a config file
class_count=10
day_start_time=815
day_end_time=1555
break_length=10 # time between classes
lunch_start=1105
lunch_end=1205
class_duration=50 # minutes

def set_default_class_duration(duration):
    class_duration=duration

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

# Right now, we make more classes than we need so that Z3 can be free to choose
# the right class for each constraint. later, we'll remove the unused class objects
classes = [Const("class_%s" % (i + 1), SchClass) for i in range(class_count)]

# We setup some shortcuts to the accessors in the class constructor above just to make
# coding easier and more readable
def teacher(i):
    return SchClass.teacher(classes[i])

def room(i):
    return SchClass.room(classes[i])

def course(i):
    return SchClass.course(classes[i])

def time(i):
    return SchClass.time(classes[i])

def students(i):
    return SchClass.students(classes[i])

# integer scope in z3 isn't the same as in python, we have to give each 
# integer a unique name in the constructor to prevent collisions in the solver.
# we'll use a helper method to make this easier
cur_name_int = 0
def next_int_name():
    global cur_name_int
    cur_name_int += 1
    return "x%s" % cur_name_int

def max_class_size(course_id=None, classroom_id=None):
    """ 
    Determines the maximum student count based on the given course and/or classroom.
    The max count is the lesser of the two if both course and classroom are given.
    """
    
    course = Course.query.get(course_id)
    classroom = Classroom.query.get(classroom_id)

    if course and course.max_student_count:
        if clasroom and clasroom.max_student_count:
            return min(course.max_student_count, clasroom.max_student_count)
        else:
            return course.max_student_count
    else:
        if classroom and classroom.max_student_count:
            return classroom.max_student_count
    return None

# ensures the teacher, room, and course ids are valid
def ensure_valid_ids():

    teacher_ids = [t.id for t in Teacher.query.all()]
    room_ids = [r.id for r in Classroom.query.all()]
    course_ids = [c.id for c in Course.query.all()]
    student_ids = [s.id for s in Student.query.all()]

    # this basically loops through each class, and then each of the lists above and makes
    # an 'assert equal' for each. The lists are put in an 'Or' constraint to ensure
    # each entry appears in the respective id list
    cons_list = [ And(Or([teacher(i) == t_id for t_id in teacher_ids]),
                      Or([room(i) == r_id for r_id in room_ids]),
                      Or([course(i) == c_id for c_id in course_ids]))
                  for i in range(class_count)]

    # make sure valid student IDs are selected. 
    x = Int(next_int_name())
    cons_list += [ ForAll(x, Or([students(i)[x] == j for j in student_ids]))
                    for i in range(class_count) ]

    return cons_list

def ensure_valid_class_durations():
    """ returns a list of z3 constraints to make sure each class is either its
        specified duration or the default duration """
    cons_list = []
    for c in Course.query.all():
        if c.duration:
            cons_list += [ If(course(i) == c.id, 
                              TimeBlock.end(time(i)) - TimeBlock.start(time(i)) == c.duration,
                              True) for i in range(class_count) ]
        else:
            cons_list += [ If(course(i) == c.id, 
                              TimeBlock.end(time(i)) - TimeBlock.start(time(i)) == class_duration,
                              True) for i in range(class_count) ] 
    return cons_list

def ensure_valid_class_start_times():
    """ returns a list of z3 constraints to make sure each class falls into a valid start time """
    # calculate the valid start times based on the config vars
    start_times = []
    cur_time = day_start_time
    while cur_time < lunch_start:
        start_times.append(cur_time)
        cur_time += class_duration + break_length

    cur_time = lunch_end
    while cur_time < day_end_time:
        start_times.append(cur_time)
        cur_time += class_duration + break_length

    return [ Or([TimeBlock.start(time(i)) == s for s in start_times]) for i in range(class_count) ]

def ensure_lunch_period():
    """ returns a list of z3 constraints making sure no class falls within the lunch period """
    return [ Or(TimeBlock.start(time(i)) >= lunch_end, TimeBlock.end(time(i)) <= lunch_start) 
             for i in range(class_count) ]

# prevent a room from being assigned to two classes that occur at the same time
def prevent_room_time_collision():
    return [ If(And(i != j, room(i) == room(j)),
                 Not( Or( And( TimeBlock.start(time(i)) <= TimeBlock.start(time(j)), 
                               TimeBlock.end(time(i)) >= TimeBlock.end(time(j)) ),
                          And( TimeBlock.start(time(i)) <= TimeBlock.start(time(j)), 
                               TimeBlock.end(time(i)) >= TimeBlock.start(time(j)) ),
                          And( TimeBlock.start(time(i)) <= TimeBlock.end(time(j)),
                               TimeBlock.end(time(i)) >= TimeBlock.end(time(j)) ))),  # then
                 True)  # else
              for i in range(class_count) for j in range(class_count) ]

# prevent a teacher from being assigned to two classes that occur at the same time
def prevent_teacher_time_collision():
    return [ If(And(i != j, teacher(i) == teacher(j)), 
                Not(time(i) == time(j)),
                True)
            for i in range(class_count) for j in range(class_count)]

# prevent a student from being assigned to two classes that occur at the same time
def prevent_student_time_collision():
    x2 = Int(next_int_name())   
    x3 = Int(next_int_name())
    return [If(And(i != j, time(i) == time(j)),
                 ForAll([x2, x3], students(i)[x2] != students(j)[x3]), True)
              for i in range(class_count) for j in range(class_count)]

# prevent the same student from being assigned into the class twice
def prevent_duplicate_student():
    x = Int(next_int_name())
    y = Int(next_int_name())
    return [If(x != y, students(i)[x] != students(i)[y], True) for i in
              range(class_count)]

def constrain_course_rooms():
    """ returns a list of z3 constraints for relationships between courses and rooms. """
    
    cons_models = ClassroomsCourse.query.all()
    cons_list = []
    # we need to construct a big 'OR' clause for each course that has 
    # all the available rooms. We'll restructure the data to make this easier
    mod_map = {}
    for mod in cons_models:
        if mod.course_id not in mod_map:
            mod_map[mod.course_id] = [mod.room_id]
        else:
            mod_map[mod.course_id].append(mod.room_id)

    # now we can loop through the map's keys and add the constraints
    for course_id in mod_map.iterkeys():

        # the rooms aren't grouped in the DB so we look through all the models and 
        # construct a list of rooms available to this course.
        cons_list += [ If( course(i) == course_id, 
                           Or([ room(i) == room_id for room_id in mod_map[course_id] ]), 
                           True )  
                        for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]
    return cons_list

def constrain_teacher_time():
    """ returns a list of z3 constraints for each teacher's available time """

    cons_list = []
    # if the teacher's start and/or end properties are set than
    # add constraints, else let the defaults kick in
    for teach in Teacher.query.all():

        if teach.start_time:
            cons_list += [ If( teacher(i) == teach.id, 
                                TimeBlock.start(time(i)) >= teach.start_time, 
                                True ) 
                            for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]
        if teach.end_time:
            cons_list += [ If( teacher(i) == teach.id, 
                                TimeBlock.end(time(i)) >= teach.end_time, 
                                True ) 
                            for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]

    return cons_list

def constrain_course_size():
    """ returns a list of z3 constraints for min and max student count on each course """

    # The size if the student lists are abstract. Here we basically make sure the list returns
    # a distinct value for indices up to the min class size, then we make sure anything over 
    # the max size is NOT distinct. Then when figuring out what students are assigned to this class
    # we pull students until we start seing duplicates
    cons_list = []
    for course in Course.query.all():
        if course.min_student_count:
            cons_list += [ If( course(i) == course.id, 
                               Distinct([ students(i)[j] for j in range(course.min_student_count)]), 
                               True) 
                            for i in range(CLASS_COUNT)]
        if course.max_student_count:
            cons_list += [ If( course(i) == course.id, 
                                Not(Distinct([ students(i)[j] for j in range(course.max_student_count)])), 
                                True) 
                            for i in range(CLASS_COUNT)]
    return cons_list

def constrain_student_req_courses():
    """ returns a list of z3 constraints for courses a student must take """

    cons_list = []
    # constraints of students to courses can come as direct relationships between students and 
    # courses, or by the student being a member of a student group that has a constraint 
    # relationship with the course. 
    for cs in CoursesStudent.query.all():
        x = Int(next_int_name())
        cons_list += [ Or([ And(course(i) == cs.course_id, students(i)[x] == cs.student_id) 
                       for i in range(CLASS_COUNT) ]) ]

    for c_grp in CoursesStudentGroup.query.all():
        for stud in c_grp.student_group.students:
            x = Int(next_int_name())
            cons_list += [ Or([ And(course(i) == c_grp.course_id, students(i)[x] == stud.id) 
                           for i in range(CLASS_COUNT) ]) ]


def make_schedule():
    
    constraints = []
    # all classes must be distinct
    # constraints = [Distinct([classes[i] for i in range(class_count)])]

    # Now we'll start adding constraints. The first set are implied constraints like
    # a teacher can't be in two places at one time.
    constraints += ensure_valid_ids()
    constraints += ensure_valid_class_durations()
    constraints += ensure_valid_class_start_times()
    constraints += ensure_lunch_period()
    constraints += prevent_room_time_collision()
    constraints += prevent_teacher_time_collision()
    constraints += prevent_student_time_collision()
    constraints += prevent_duplicate_student()

    # next, include the user provided constraints


  

    # Finally, ask the solver to give us a schedule and then parse the results
    s = Solver()
    s.add(constraints)
    if s.check() != sat:
        raise SchedulerNoSoltuion()
    else:
        m = s.model()
        for i in range(class_count):
            c = ScheduledClass(int(str(m.evaluate(course(i)))), 
                               int(str(m.evaluate(room(i)))),
                               int(str(m.evaluate(teacher(i)))),
                               int(str(m.evaluate(TimeBlock.start(time(i))))),
                               int(str(m.evaluate(TimeBlock.end(time(i))))))
        
        # # now add the students to the new class. the z3 arrays are undefined length (they will return values
        # # for any index we give them.) we'll pull values until the max class size after that the values should
        # # voilate the unique constraint.
        # for j in range(max_class_size(m.evaluate(course(i)), m.evaluate(room(i)))):
        #     ScheduledClassesStudent(student_id=m.evaluate(students(i)[j]), scheduled_class_id=c.id) 

        


