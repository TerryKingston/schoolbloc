if __name__ == '__main__':
	from z3 import *

	# teachers, classrooms, and subjects
	# classrooms and subjects are arrays
	# and teachers are integer values
	TEACHER_COUNT = 6
	ROOM_COUNT = 6
	SUBJECT_COUNT = 4



	# classrooms->teacher. teachers are represented by an integer
	rooms_teachers = [ Int("room_%s_teacher" % (i+1)) for i in range(ROOM_COUNT) ]

	# teacher->subject. teachers are represented by an integer
	teachers_subjects = [ Int("teacher_%s_subject" % (i+1)) for i in range(TEACHER_COUNT) ]

	# each classroom must have a teacher
	fill_c_rooms_c = [ And(1 <= rooms_teachers[i], rooms_teachers[i] <= TEACHER_COUNT) for i in range(TEACHER_COUNT) ]

	# each teacher must have a subject
	fill_subs_c = [ And(1 <= teachers_subjects[i], teachers_subjects[i] <= SUBJECT_COUNT) for i in range(SUBJECT_COUNT)]

	# all subjects must be taught
	# TODO

	# each classroom must have a distinct teacher
	match_c = [ Distinct([rooms_teachers[i] for i in range(TEACHER_COUNT) ]) ]


	# collect the constraints on the model properties
	model_c = fill_c_rooms_c + fill_subs_c + match_c

	
	# now we add the constraints specific to the schedule (the user added constraints)

	# add some constraints on teacher/classroom relationships
	teach_class_c = [ 
		# teacher 1 can teach in room 2, 3, or 5
		Or(rooms_teachers[1] == 1, rooms_teachers[2] == 1, rooms_teachers[4] == 1),
		# teacher 2 must teach in 5
		rooms_teachers[4] == 2]

	# constraints on the teacher/subject relationships
	teach_sub_c = [
		# teacher 1 can teach subjects 1 and 3
		Or(teachers_subjects[0] == 1, teachers_subjects[2] == 1),
		# teacher 4 can teach subject 4
		teachers_subjects[3] == 4]

	# finally, add constraints on the subject/classroom relationships

	# subject 2 can be taught in clas

	schedule_c = teach_class_c + teach_sub_c

	s = Solver()
	s.add(model_c + schedule_c)
	if s.check() == sat:
		m = s.model()
		print m

		# print the result in an easy to read format
		for i in range(TEACHER_COUNT):
			# find each teacher, then the room they will use and the subject they will teach
			print "Teacher: ", i + 1
			print "Subject: ", m.evaluate(teachers_subjects[i])

			# search through the rooms for this teacher
			for j in range(ROOM_COUNT):
				r = int(str(m.evaluate(rooms_teachers[j])))
				if r == (i + 1):
					print "Room: ", j + 1
					
			print ""


			
	else:
		print "failed to solve"
