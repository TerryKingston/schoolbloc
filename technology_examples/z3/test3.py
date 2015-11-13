if __name__ == '__main__':
	from z3 import *

	# Teachers, Classrooms, Subjects, Time
	# This time in a 4-D array (one dimension for each type)
	# we'll put a bool in each position, true means there is a mapping of teacher-classroom

	TEACHER_COUNT = 6
	ROOM_COUNT = 6
	TIME_COUNT = 4
	SUBJECT_COUNT = 3

	# build the array
	X = [ [ [ [ Int("teacher_%s_room_%s_subject_%s_time_%s" % (teacher+1, room+1, subject+1, time+1)) 
							for subject in range(SUBJECT_COUNT)]
							for time in range(TIME_COUNT)]
							for room in range(ROOM_COUNT)]
							for teacher in range(TEACHER_COUNT)]

	# each cell contains 1 or 0
	cells_c = [ Or(X[teacher][room][time][subject] == 1, X[teacher][room][time][subject] == 0) 
							for teacher in range(TEACHER_COUNT) 
							for room in range(ROOM_COUNT) 
							for time in range(TIME_COUNT) 
							for subject in range(SUBJECT_COUNT)]

	# each teacher-time-subject has exactly one room
	con_1 = [ Sum([X[teacher][room][time][subject] for room in range(ROOM_COUNT)]) == 1 
											for teacher in range(TEACHER_COUNT) 
											for time in range(TIME_COUNT)
											for subject in range(SUBJECT_COUNT) ] 

	# each room-time-subject has exactly one teacher
	con_2 = [ Sum([X[teacher][room][time][subject] for teacher in range(TEACHER_COUNT)]) == 1 
											for room in range(ROOM_COUNT)
											for time in range(TIME_COUNT)
											for subject in range(SUBJECT_COUNT)]

	# each time-subject-teacher has exactly one room
	con_3 = [ Sum([X[teacher][room][time][subject] for room in range(ROOM_COUNT)]) == 1 
											for teacher in range(TEACHER_COUNT)
											for time in range(TIME_COUNT)
											for subject in range(SUBJECT_COUNT)]

	# each teacher-room-time has exactly one subject
	con_4 = [ Sum([X[teacher][room][time][subject] for subject in range(SUBJECT_COUNT)]) == 1 
											for teacher in range(TEACHER_COUNT)
											for time in range(TIME_COUNT)
											for room in range(ROOM_COUNT)]




	model_cons = cells_c + con_1 + con_2 + con_3 + con_4

	s = Solver()
	s.add(model_cons)
	if s.check() == sat:
		m = s.model()
		for teacher in range(TEACHER_COUNT):
			for room in range(ROOM_COUNT):
				for time in range(TIME_COUNT):
					for subject in range(SUBJECT_COUNT):
						r = str(m.evaluate(X[teacher][room][time][subject]))
						if r == "1":
							print "Teacher: ", teacher+1, " room: ", room+1, " time: ", time+1, " subject: ", subject+1
	else:
		print "Failed to solve!"