if __name__ == '__main__':
	from z3 import *

	# teachers and classrooms
	# we'll match up teachers and classrooms
	# classrooms are positions in the array
	# and teachers are integer values

	# classrooms represented by an array of 6 values
	c_rooms = [ Int("r_%s" % (i+1)) for i in range(6) ]

	# each classroom must have a teacher
	teach_c = [ And(1 <= c_rooms[i], c_rooms[i] <= 6) for i in range(6) ]

	# each classroom must have a different teacher
	match_c = [ Distinct([c_rooms[i] for i in range(6) ]) ]

	# add some constraints on teacher/classroom relationships
	teach_class_c = [ 
		# teacher 1 can teach in room 2, 3, or 5
		Or(c_rooms[1] == 1, c_rooms[2] == 1, c_rooms[4] == 1),
		# teacher 2 must teach in 5
		c_rooms[4] == 2]

	s = Solver()
	s.add(teach_c + match_c + teach_class_c)
	print s.check()
	print s.model()