class ScheduleGenerator:
	""" The Schedule Generator creates a school 
		schedule from DB information and then stores 
		the generated schedule into the DB """

	from z3 import *
	from schoolbloc.users.models import *
	from schoolbloc.teachers.models import *
	from schoolbloc.rooms.models import *
	from schoolbloc.times.models import *
	from schoolbloc.students.models import *

	
	def make_schedule():
		# make the class z3 data type and define its constructor
		# a class represents a mapping of teacher, room, course, time, and students
		# Z3 will choose integers for teacher, room, course, and time. Its our job to 
		# restrict the choices of integer to only valid IDs of correspoding DB objects
		Class = Datatype('Class')
		Class.declare('Class', ('teacher', IntSort()),
							   ('room', IntSort()),
							   ('time', IntSort()),
							   ('students'), ArraySort(IntSort(), IntSort()))

		# we also need to make a TimeBlock Class because the start and end time properties matter
		# when determining the schedule
		TimeBlock = Datatype('TimeBlock')
		TimeBlock.declare('start_end', ('start', IntSort()), ('end', IntSort()))


		TimeBlock, Class = CreateDatatypes(TimeBlock, Class)

		# Right now, we make more classes than we need so that Z3 can be free to choose 
		# the right class for each constraint. later, we'll remove the unused class objects
		CLASS_COUNT = 10
		classes = [Const("class_%s" % (i+1), Class) for i in range(CLASS_COUNT)]

		# We setup some shortcuts to the accessors in the class constructor above just to make
		# coding easier and more readable
		def teacher(i):
		return Class.teacher(classes[i])

		def room(i):
			return Class.room(classes[i])

		def course(i):
			return Class.course(classes[i])

		def time(i):
			return Class.time(classes[i])

		def students(i):
			return Class.students(classes[i])

		# all classes must be distinct
		dist_c = [Distinct([classes[i] for i in range(CLASS_COUNT)])]


		# Now we'll start adding constraints. The first set are implied constraints like
		# a teacher can't be in two places at one time.

		# First, make sure z3 picks valid ids for teachers, rooms, etc...
		teach_list = Teacher.query.all()
		teacher_ids = [ teach_list[i].id for i in range(len(teach_list)) ]

		room_list = Room.query.all()
		teacher_ids = [ room_list[i].id for i in range(len(room_list)) ]

		time_list = Time.query.all()
		teacher_ids = [ time_list[i].id for i in range(len(time_list)) ]

		st_list = Student.query.all()
		teacher_ids = [ st_list[i].id for i in range(len(st_list)) ]

		# this basically loops through each class, and then each of the lists above and makes
		# an 'assert equal' for each. The lists are put in an 'Or' constraint to ensure
		# each entry appears in the respective id list
		mod_c = [ And( Or([ teacher(i) == t_id for t_id in teacher_ids ]), 
					   Or([ room(i) == r_id for r_id in room_ids ]),
					   Or([ course(i) == c_id for c_id in course_ids ]),
					   Or([ time(i) == t_id for t_id in time_ids ]))
				  for i in range(CLASS_COUNT) ]

		# make sure valid student IDs are selected
		x1 = Int('x1')
		mod_c += [ ForAll(x1, Or([ students(i)[x1] == j for j in student_ids ]) ) for i in range(CLASS_COUNT) ]

		# now make sure two classes aren't in the same room at the same time
		mod_c += [ If( And( i != j, room(i) == room(j)), 
								Not( time(i) == time(j) ), # then
								True ) # else
							 for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]


		# make sure each teacher only teaches one class at a time
		mod_c += [ If( And( i != j, teacher(i) == teacher(j)), Not( time(i) == time(j) ), True ) 
							 for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]

		# the same student can't be in the class twice
		x = Int('x')
		y = Int('y')
		mod_c += [ If( x != y, students(i)[x] != students(i)[y], True) for i in range(CLASS_COUNT) ]

		# every course must be represented
		mod_c += [ Or([course(j) == i for j in range(CLASS_COUNT)]) for i in course_ids ]

		# a student can't be in two classes at the same time
		x2 = Int('x2')
		x3 = Int('x3')
		mod_c += [ If ( And( i != j, time(i) == time(j) ), 
									ForAll([x2, x3], students(i)[x2] != students(j)[x3]), True ) 
							 for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]

