if __name__ == '__main__':
	from z3 import *

	# Teachers, Classrooms
	# This time in a 2-D array (one dimension for each type)
	# we'll put a bool in each position, true means there is a mapping of teacher-classroom

	TEACHER_COUNT = 6
	ROOM_COUNT = 6

	# build the array
	X = [ [ Int("teacher_%s_room_%s" % (teacher+1, room+1)) 
					for room in range(ROOM_COUNT)]
					for teacher in range(TEACHER_COUNT)]

	# each cell contains 1 or 0
	cells_c = [ Or(X[teacher][room] == 1, X[teacher][room] == 0) 
							for teacher in range(TEACHER_COUNT) 
							for room in range(ROOM_COUNT) ]

	# each teacher has exactly one room
	one_teacher_room = [ Sum(X[teacher]) == 1 for teacher in range(TEACHER_COUNT) ] 
	one_room_teach = [ Sum([X[teacher][room] for teacher in range(TEACHER_COUNT)]) == 1 for room in range(ROOM_COUNT)]

	model_cons = cells_c + one_teacher_room + one_room_teach

	s = Solver()
	s.add(model_cons)
	if s.check() == sat:
		m = s.model()
		for teacher in range(TEACHER_COUNT):
			for room in range(ROOM_COUNT):
				r = str(m.evaluate(X[teacher][room]))
				if r == "1":
					print "Teacher: ", teacher + 1, " room: ", room + 1
	else:
		print "Failed to solve!"