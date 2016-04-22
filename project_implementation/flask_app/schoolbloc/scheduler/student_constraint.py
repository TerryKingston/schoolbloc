from schoolbloc.scheduler.models import *

class StudentConstraint:
	def __init__(self, student_id):
		self.student_id = student_id

		self.calc_constraints()

	def relax_constraints(self, class_id):
		if len(self.mand_course_ids) == 0 and len(self.high_course_ids) > 0:
			SchedUtil.log_note("info", "Scheduler", "Relaxing the student->course constraints for student {} ".format(
                self.student_id))
			self.high_course_ids = []
			return 

		return False

	def can_relax_constraints(self):
		return len(self.mand_course_ids) == 0 and len(self.high_course_ids) > 0

	def get_course_ids(self, count):
		"""
		Returns the list of required courses. All mandatory ids are returned, but after that, 
		if the student is underscheduled, then the remaining count is filled with high and then low priority 
		courses
		"""
		result_ids = list(self.mand_course_ids)
		remaining_count = count - len(result_ids)
		if remaining_count <= 0:
			return result_ids
		
		result_ids += self.high_course_ids[:remaining_count]
		remaining_count -= len(self.high_course_ids)

		if remaining_count <= 0:
			return result_ids

		result_ids += self.low_course_ids[:remaining_count]
		remaining_count -= len(self.low_course_ids)

		return result_ids


	def calc_constraints(self):
		"""
		Pulls the constraints related to this student from the database
		"""
		ss_list = StudentsStudentGroup.query.filter_by(student_id=self.student_id).all()
		self.student_group_ids = [ ss.student_group_id for ss in ss_list ]

		
		self.mand_course_ids = [ ct.course_id 
							for ct in CoursesStudent.query.filter_by(student_id=self.student_id,
																	 priority="mandatory") ]
		self.high_course_ids = [ ct.course_id 
							for ct in CoursesStudent.query.filter_by(student_id=self.student_id,
																	 priority="high") ]
		self.low_course_ids = [ ct.course_id 
						   for ct in CoursesStudent.query.filter_by(student_id=self.student_id,
																	priority="low") ]

		# now collect the courses assigned to the student through their subjects
		for ss in StudentsSubject.query.filter_by(student_id=self.student_id, priority="mandatory"):
			# if a course is not already assigned to the student through a direct constraint, we choose
			# one of the courses in the subject
			course_ids = [ cs.course_id for cs in CoursesSubject.query.filter_by(subject_id=ss.subject_id) ]
			if len(course_ids) > 0 and set(course_ids) & set(self.mand_course_ids) == set():
				self.mand_course_ids.append(course_ids[0])

		for ss in StudentsSubject.query.filter_by(student_id=self.student_id, priority="high"):
			course_ids = [ cs.course_id for cs in CoursesSubject.query.filter_by(subject_id=ss.subject_id) ]
			if len(course_ids) > 0 and set(course_ids) & set(self.high_course_ids) == set():
				self.high_course_ids.append(course_ids[0])

		for ss in StudentsSubject.query.filter_by(student_id=self.student_id, priority="low"):
			course_ids = [ cs.course_id for cs in CoursesSubject.query.filter_by(subject_id=ss.subject_id) ]
			if len(course_ids) > 0 and set(course_ids) & set(self.low_course_ids) == set():
				self.low_course_ids.append(course_ids[0])

		# now collect the courses assigned to the student through the student groups, but make sure
		# we're not adding the same id twice
		for sg_id in self.student_group_ids:
			for csg in CoursesStudentGroup.query.filter_by(student_group_id=sg_id, priority="mandatory"):
				if csg.course_id not in self.mand_course_ids:
					self.mand_course_ids.append(csg.course_id)
			
			for csg in CoursesStudentGroup.query.filter_by(student_group_id=sg_id, priority="high"):
				if csg.course_id not in self.high_course_ids:
					self.high_course_ids.append(csg.course_id)
			
			for csg in CoursesStudentGroup.query.filter_by(student_group_id=sg_id, priority="low"):
				if csg.course_id not in self.low_course_ids:
					self.low_course_ids.append(csg.course_id)

		# now collect the courses assigned to the student through subjects assigend to the student group
		for sg_id in self.student_group_ids:
			for ss in StudentGroupsSubject.query.filter_by(student_group_id=sg_id, priority="mandatory"):
				# if a course is not already assigned to the student through a direct constraint, we choose
				# one of the courses in the subject
				course_ids = [ cs.course_id for cs in CoursesSubject.query.filter_by(subject_id=ss.subject_id) ]
				if len(course_ids) > 0 and set(course_ids) & set(self.mand_course_ids) == set():
					self.mand_course_ids.append(course_ids[0])

			for ss in StudentGroupsSubject.query.filter_by(student_group_id=sg_id, priority="high"):
				course_ids = [ cs.course_id for cs in CoursesSubject.query.filter_by(subject_id=ss.subject_id) ]
				if len(course_ids) > 0 and set(course_ids) & set(self.high_course_ids) == set():
					self.high_course_ids.append(course_ids[0])

			for ss in StudentGroupsSubject.query.filter_by(student_group_id=sg_id, priority="low"):
				course_ids = [ cs.course_id for cs in CoursesSubject.query.filter_by(subject_id=ss.subject_id) ]
				if len(course_ids) > 0 and set(course_ids) & set(self.low_course_ids) == set():
					self.low_course_ids.append(course_ids[0])


