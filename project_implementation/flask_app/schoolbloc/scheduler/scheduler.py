from z3 import *
from schoolbloc.users.models import User
from schoolbloc.teachers.models import Teacher
from schoolbloc.classrooms.models import Classroom
from schoolbloc.students.models import Student
from schoolbloc.scheduled_classes.models import ScheduledClass


class SchedulerNoSoltuion(Exception):
    pass

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
current = 0
def next_int_name():
    name = "x%s" % current
    curent += 1
    return name

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

    teach_list = Teacher.query.all()
    teacher_ids = [teach_list[i].id for i in range(len(teach_list))]

    room_list = Room.query.all()
    teacher_ids = [room_list[i].id for i in range(len(room_list))]

    st_list = Student.query.all()
    teacher_ids = [st_list[i].id for i in range(len(st_list))]

    # this basically loops through each class, and then each of the lists above and makes
    # an 'assert equal' for each. The lists are put in an 'Or' constraint to ensure
    # each entry appears in the respective id list
    cons = [And(Or([teacher(i) == t_id for t_id in teacher_ids]),
                Or([room(i) == r_id for r_id in room_ids]),
                Or([course(i) == c_id for c_id in course_ids]))
            for i in range(class_count)]

    # make sure valid student IDs are selected. 
    x = Int(next_int_name())
    cons += [ForAll(x1, Or([students(i)[x] == j for j in student_ids]))
              for i in range(class_count)]

    return cons

# prevent a room from being assigned to two classes that occur at the same time
def prevent_room_time_collision():
    return [ If(And(i != j, room(i) == room(j)),
                 Not(time(i) == time(j)),  # then
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
    mod_c += [If(x != y, students(i)[x] != students(i)[y], True) for i in
              range(class_count)]


def make_schedule(class_count=10):
    
    # Right now, we make more classes than we need so that Z3 can be free to choose
    # the right class for each constraint. later, we'll remove the unused class objects
    classes = [Const("class_%s" % (i + 1), SchClass) for i in range(class_count)]

    # all classes must be distinct
    # dist_c = [Distinct([classes[i] for i in range(class_count)])]

    # Now we'll start adding constraints. The first set are implied constraints like
    # a teacher can't be in two places at one time.
    constraints = ensure_valid_ids()
    constraints += prevent_room_time_collision()
    constraints += prevent_teacher_time_collision()
    constraints += prevent_student_time_collision()
    constraints += prevent_duplicate_student()

  

    # Finally, ask the solver to give us a schedule and then parse the results
    s = Solver()
    s.add(constraints)
    if s.check() != sat:
        raise SchedulerNoSoltuion()

    m = s.model()
    for i in range(class_count):
        c = ScheduledClass(teacher=m.evaluate(teacher(i)), 
                           room=m.evaluate(room(i)),
                           course=m.evaluate(course(i)),
                           time=m.evaluate(time(i)) )
        
        # now add the students to the new class. the z3 arrays are undefined length (they will return values
        # for any index we give them.) we'll pull values until the max class size after that the values should
        # voilate the unique constraint.
        for j in range(max_class_size(m.evaluate(course(i)), m.evaluate(room(i)))):
            ScheduledClassesStudent(student_id=m.evaluate(students(i)[j]), scheduled_class_id=c.id) 

        log.info('added new class: teacher={} {}, room={}, course={}, time={}, students={}'.format(
            c.teacher_id, c.classroom_id, c.course_id, c.time_id, [ student.id for student in c.students ]))


