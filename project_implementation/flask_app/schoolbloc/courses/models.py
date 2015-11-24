import logging
from schoolbloc import db

log = logging.getLogger(__name__)

class CourseError(Exception):
	pass

class Course(db.Model):
	"""
	ORM object for courses stored in the database

	A course is a specific learning area (i.e. Algebra III)
	"""

	__tablename__ = 'courses'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), nullable=False)
	max_student_count = db.Column(db.Integer)
	min_student_count = db.Column(db.Integer)

	def __init__(self, name, **other_params):

		self.name = name
		if ('max_student_count' in other_params):
			self.max_student_count = other_params['max_student_count']

		if ('min_student_count' in other_params):
			self.min_student_count = other_params['min_student_count']

		db.session.add(self)
		db.session.commit()
		log.info('added new course: {}'.format(name))

	def __repr__(self):
		return "<name={} max_student_count={} min_student_count={}>".format(self.name, self.max_student_count, self.min_student_count)

	def delete(self):
		db.session.delete(self)
		db.session.commit()

class CoursesStudentError(Exception):
	pass

class CoursesStudent(db.Model):
	"""
	ORM object for linking table between courses and students tables

	A CoursesStudent describes the relationship constraints 
	between a course and a student for the scheduler. 

	The actual assignment of a course to a student happens in 
	the Class object.
	"""

	__tablename__ = 'courses_students'
	id = db.Column(db.Integer, primary_key=True)
	course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
	course = db.relationship("Course", backref="courses_students")
	student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
	student = db.relationship("Student", backref="courses_students")
	active = db.Column(db.Boolean, nullable=False, default=True)

	def __init__(self, course_id, student_id, **other_params):

		# we want to verify the given id's are actually present in the DB
		if (Course.query.get(course_id) == None):
			raise CoursesStudentError("The course_id {} does not exist in the db".format(course_id))

		from schoolbloc.students.models import Student
		student = Student.query.get(student_id)
		if (student == None):
			raise CoursesStudentError("The student_id {} does not exist in the db".format(student_id))

		self.course_id = course_id
		self.student_id = student_id
		if ('active' in other_params):
			self.active = other_params['active']

		db.session.add(self)
		db.session.commit()
		log.info('acced new CoursesStudent: {} <--> {} {}'.format(course.room_number, 
																  student.first_name, 
																  student.last_name) )
	def __repr__(self):
		return "<course_id={} student_id={}>".format(self.course_id, self.student_id)

	def delete(self):
		db.sesson.delete(self)
		db.session.commit()

class CoursesTeacherError(Exception):
	pass

class CoursesTeacher(db.Model):
	"""
	ORM object for linking table between courses and teachers tables

	A CoursesTeacher describes the relationship constraints 
	between a course and a teacher for the scheduler. 

	The actual assignment of a course to a teacher happens in 
	the Class object.
	"""

	__tablename__ = 'courses_teachers'
	id = db.Column(db.Integer, primary_key=True)
	course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
	course = db.relationship("Course", backref="courses_teachers")
	teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
	teacher = db.relationship("Teacher", backref="courses_teachers")
	active = db.Column(db.Boolean, nullable=False, default=True)

	def __init__(self, course_id, teacher_id, **other_params):

		# we want to verify the given id's are actually present in the DB
		if (Course.query.get(course_id) == None):
			raise CoursesTeacherError("The course_id {} does not exist in the db".format(course_id))

		from schoolbloc.teachers.models import Teacher
		teacher = Teacher.query.get(teacher_id)
		if (teacher == None):
			raise CoursesTeacherError("The teacher_id {} does not exist in the db".format(teacher_id))

		self.course_id = course_id
		self.teacher_id = teacher_id
		if ('active' in other_params):
			self.active = other_params['active']

		db.session.add(self)
		db.session.commit()
		log.info('acced new CoursesTeacher: {} <--> {} {}'.format(course.room_number, 
																  teacher.first_name, 
																  teacher.last_name) )
	def __repr__(self):
		return "<course_id={} teacher_id={}>".format(self.course_id, self.teacher_id)

	
	def delete(self):
		db.sesson.delete(self)
		db.session.commit()

class CoursesStudentGroupError(Exception):
	pass

class CoursesStudentGroup(db.Model):
	"""
	ORM object for linking table between courses and student groups tables

	A CoursesStudentGroup describes the relationship constraints 
	between a course and a student group for the scheduler. 

	The actual assignment of a course to a student group happens in 
	the Class object.
	"""

	__tablename__ = 'courses_student_groups'
	id = db.Column(db.Integer, primary_key=True)
	course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
	course = db.relationship("Course", backref="courses_student_groups")
	student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
	student_group = db.relationship("StudentGroup", backref="courses_student_groups")
	active = db.Column(db.Boolean, nullable=False, default=True)

	def __init__(self, course_id, student_group_id, **other_params):

		# we want to verify the given id's are actually present in the DB
		if (Course.query.get(course_id) == None):
			raise CoursesStudentGroupError("The course_id {} does not exist in the db".format(course_id))

		from schoolbloc.student_groups.models import StudentGroup
		student_group = StudentGroup.query.get(student_group_id)
		if (student_group == None):
			raise CoursesStudentGroupError("The student_group_id {} does not exist in the db".format(student_group_id))

		self.course_id = course_id
		self.student_group_id = student_group_id
		if ('active' in other_params):
			self.active = other_params['active']

		db.session.add(self)
		db.session.commit()
		log.info('acced new CoursesStudentGroup: {} <--> {} {}'.format(course.room_number, student_group.name) )
	
	def __repr__(self):
		return "<course_id={} student_group_id={}>".format(self.course_id, self.student_group_id)

	def delete(self):
		db.sesson.delete(self)
		db.session.commit()

class CoursesSubjectError(Exception):
	pass

class CoursesSubject(db.Model):
	"""
	ORM object for linking table between courses and subjects tables

	A CoursesSubject describes the relationship constraints 
	between a course and a subject for the scheduler. 

	The actual assignment of a course to a subject happens in 
	the Class object.
	"""

	__tablename__ = 'courses_subjects'
	id = db.Column(db.Integer, primary_key=True)
	course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
	course = db.relationship("Course", backref="courses_subjects")
	subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
	subject = db.relationship("Subject", backref="courses_subjects")
	active = db.Column(db.Boolean, nullable=False, default=True)

	def __init__(self, course_id, subject_id, **other_params):

		# we want to verify the given id's are actually present in the DB
		if (Course.query.get(course_id) == None):
			raise CoursesSubjectError("The course_id {} does not exist in the db".format(course_id))

		from schoolbloc.subjects.models import Subject
		subject = Subject.query.get(subject_id)
		if (subject == None):
			raise CoursesSubjectError("The subject_id {} does not exist in the db".format(subject_id))

		self.course_id = course_id
		self.subject_id = subject_id
		if ('active' in other_params):
			self.active = other_params['active']

		db.session.add(self)
		db.session.commit()
		log.info('acced new CoursesSubject: {} <--> {} {}'.format(course.room_number, subject.name) )
	
	def __repr__(self):
		return "<course_id={} subject_id={}>".format(self.course_id, self.subject_id)

	def delete(self):
		db.sesson.delete(self)
		db.session.commit()