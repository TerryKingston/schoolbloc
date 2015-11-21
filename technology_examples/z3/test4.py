if __name__ == '__main__':
	from z3 import *

	# use Z3 custom types to define a 'Class' which is
	# an actual class instance with an assigned Teacher, Students, Course and Time

	Time = Datatype('Time')
	Time.declare('start_end', ('start', IntSort()), ('end', IntSort()))
	Time.create()


	# make the class data type
	Class = Datatype('Class')
	# define the constructor. 
	# constructor name first, then params are passed in name-type pairs. eg. ('id', IntSort())
	# the params are turned into accessors
	Class.declare('tch_rm_crse_tme', ('teacher', IntSort()), 
																	 ('room', IntSort()), 
																	 ('course', IntSort()), 
																	 ('time', Time),
																	 ('students', ArraySort( IntSort(), IntSort())))
	Time, Class = CreateDatatypes(Time, Class)	

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


	# all classes must be distinct
	dist_c = [Distinct([classes[i] for i in range(CLASS_COUNT)])]

	# make sure valid teachers, rooms, courses, and times are assigned
	# example data below, this data should represent DB object ids
	teacher_ids = [1, 2, 3, 4, 5, 6, 7]
	student_ids = range(1, 50)
	room_ids = [100, 105, 110, 115, 200, 205, 210, 215]
	course_ids = [1100, 3100, 2010, 2000, 2005, 2200]

	# this basically loops through each class, and then each of the lists above and makes
	# an 'assert equal' for each. The lists are put in an 'Or' constraint to ensure
	# each entry appears in the respective id list
	mod_c = [ And( Or([ teacher(i) == t_id for t_id in teacher_ids ]), 
				   Or([ room(i) == r_id for r_id in room_ids ]),
				   Or([ course(i) == c_id for c_id in course_ids ]))
			  for i in range(CLASS_COUNT)]

	# make sure the times respect the day start and end time
	mod_c += [ And(Time.start(time(i)) > 810, 
				   Time.start(time(i)) < Time.end(time(i)),
				   Time.end(time(i)) < 1625) 
			   for i in range(CLASS_COUNT) ]

	# # make sure valid student IDs are selected
	x1 = Int('x1')
	mod_c += [ ForAll(x1, Or([ students(i)[x1] == j for j in student_ids ]) ) for i in range(CLASS_COUNT) ]

	# now make sure two classes aren't in the same room at the same time
	mod_c += [ If(  And( i != j, room(i) == room(j)), 
						 Not( Or( And( Time.start(time(i)) <= Time.start(time(j)), 
									   Time.end(time(i)) >= Time.end(time(j)) ),
								  And( Time.start(time(i)) <= Time.start(time(j)), 
								   	   Time.end(time(i)) >= Time.start(time(j)) ),
								  And( Time.start(time(i)) <= Time.end(time(j)),
								   	   Time.end(time(i)) >= Time.end(time(j)) ))),
					True ) # else
				for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]


	# make sure each teacher only teaches one class at a time
	mod_c += [ If( And( i != j, teacher(i) == teacher(j)), 
						Not( Or( And( Time.start(time(i)) <= Time.start(time(j)), 
									   Time.end(time(i)) >= Time.end(time(j)) ),
								  And( Time.start(time(i)) <= Time.start(time(j)), 
								   	   Time.end(time(i)) >= Time.start(time(j)) ),
								  And( Time.start(time(i)) <= Time.end(time(j)),
								   	   Time.end(time(i)) >= Time.end(time(j)) ))),
					True ) # else
			 for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]

	# # the same student can't be in the class twice
	x = Int('x')
	y = Int('y')
	mod_c += [ If( x != y, students(i)[x] != students(i)[y], True) for i in range(CLASS_COUNT) ]

	# the same student can't be in two classes at the same time
	st_a = Int('st_a')
	st_b = Int('st_b')
	mod_c += [ If(ForAll([st_a, st_b], And(students(i)[st_a] == students(j)[st_b], Or(i != j, st_a != st_b))), 
						Not( Or( And( Time.start(time(i)) <= Time.start(time(j)), 
									   Time.end(time(i)) >= Time.end(time(j)) ),
								  And( Time.start(time(i)) <= Time.start(time(j)), 
								   	   Time.end(time(i)) >= Time.start(time(j)) ),
								  And( Time.start(time(i)) <= Time.end(time(j)),
								   	   Time.end(time(i)) >= Time.end(time(j)) ))),
					True ) # else
			 for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]


	# # every course must be represented
	mod_c += [ Or([course(j) == i for j in range(CLASS_COUNT)]) for i in course_ids ]



	# # lets try user defined constraints!

	# # course 3100 can only be in rooms 105 and 110
	mod_c += [ If( course(i) == 3100, Or(room(i) == 105, room(i) == 110), True )  
				for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]
	
	# # teacher 5 can only teach after noon
	mod_c += [ If( teacher(i) == 5, Time.start(time(i)) > 1200, True ) 
				for i in range(CLASS_COUNT) for j in range(CLASS_COUNT) ]

	# # course 2000 has min and max class size of 10 and 34 respectively
	mod_c += [ If( course(i) == 2000, Distinct([ students(i)[j] for j in range(10)]), True) 
					for i in range(CLASS_COUNT)]

	mod_c += [ If( course(i) == 2000, Not(Distinct([ students(i)[j] for j in range(14)])), True) 
						 for i in range(CLASS_COUNT)]

	# # there must be at least two classes with course 2000
	# mod_c += [ Or([ And([ i != j, course(i) == 2000, course(j) == 2000 ]) 
	# 				 			for i in range(CLASS_COUNT) for j in range(CLASS_COUNT)]) ]

	# course 2000 is required for student group 1
	# list of student IDs in student group 1
	student_grp = [2, 5, 7, 8, 12, 23, 26, 28, 29, 30, 41, 44, 45]
	
	mod_c += [ And([ Or([ And(course(i) == 2000, students(i)[Int("x_%s_%s" %(i, s_id))] == s_id)
			   for i in range(CLASS_COUNT) ]) for s_id in student_grp]) ]


	

	s = Solver()
	s.add(dist_c + mod_c)
	if s.check() == sat:
		m = s.model()
		for i in range(CLASS_COUNT):
			print "Class ", i, \
						": teacher = ", m.evaluate(teacher(i)), \
						" room =", m.evaluate(room(i)), \
						" course =", m.evaluate(course(i)), \
						" time =", m.evaluate(time(i)) 
			# now print the student list. we'll collect students until we get a repeat value
			j = 0
			s_list = []
			while int(str(m.evaluate(students(i)[j]))) not in s_list:
				s_list += [ int(str(m.evaluate(students(i)[j]))) ]
				j += 1
				
			print "Students: ", s_list, "\n"
		# print m
		# for i in range(CLASS_COUNT):
		# 	if str(m.evaluate(course(i))) == '2000':
		# 		print "Class ", i
		# 		for j in range(20):
		# 			print m.evaluate(students(i)[j])
	else:
		print "No Solution!"