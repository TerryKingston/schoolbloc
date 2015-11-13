if __name__ == '__main__':
	from z3 import *

	# use Z3 custom types to define a 'Class' which is
	# an actual class instance with an assigned Teacher, Students, Course and Time


	# make the class data type
	Class = Datatype('Class')
	# define the constructor. 
	# constructor name first, then params are passed in name-type pairs. eg. ('id', IntSort())
	# the params are turned into accessors
	Class.declare('tch_rm_crse_tme', ('teacher', IntSort()), 
																	 ('room', IntSort()), 
																	 ('course', IntSort()), 
																	 ('time', IntSort()),
																	 ('students', ArraySort( IntSort(), IntSort())))
	Class = Class.create()	

	# make the classes
	CLASS_COUNT = 10
	classes = [Const("class_%s" % (i+1), Class) for i in range(CLASS_COUNT)]

	# setup shortcuts to accessors
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

	# make the classes
	CLASS_COUNT = 10
	classes = [Const("class_%s" % (i+1), Class) for i in range(CLASS_COUNT)]

	# all classes must be distinct
	dist_c = [Distinct([classes[i] for i in range(CLASS_COUNT)])]

	# make sure valid teachers, rooms, courses, and times are assigned
	# example data below, this data should represent DB object ids
	teacher_ids = [1, 2, 3, 4, 5, 6, 7]
	student_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
	room_ids = [100, 105, 110, 115, 200, 205, 210, 215]
	course_ids = [1100, 3100, 2010, 2000, 2005, 2200]
	time_ids = [850, 910, 1025, 1345, 1415, 1455]

	# this basically loops through each class, and then each of the lists above and makes
	# an 'assert equal' for each. The lists are put in an 'Or' constraint to ensure
	# each entry appears in the respective id list
	mod_c = [ And( Or([ teacher(i) == t_id for t_id in teacher_ids ]), 
								 Or([ room(i) == r_id for r_id in room_ids ]),
								 Or([ course(i) == c_id for c_id in course_ids ]),
								 Or([ time(i) == t_id for t_id in time_ids ]))
					 for i in range(CLASS_COUNT)]

	
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

	

	# lets try user defined constraints!

	# course 3100 can only be in rooms 105 and 110
	mod_c += [ If( course(i) == 3100, Or(room(i) == 105, room(i) == 110), True )  
						 for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]
	
	# teacher 5 can only teach after noon
	mod_c += [ If( teacher(i) == 5, time(i) > 1200, True ) 
						 for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]

	# course 2000 has min and max class size of 20 and 34 respectively
	mod_c += [ If( course(i) == 2000, Distinct([ students(i)[j] for j in range(20)]), True) 
						 for i in range(CLASS_COUNT)]



	s = Solver()
	s.add(dist_c + mod_c)
	if s.check() == sat:
		print s.model()
	else:
		print "No Solution!"