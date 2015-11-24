import logging
from schoolbloc import db

log = logging.getLogger(__name__)

class StudentError(Exception):
	pass

class Student(db.Model):
	"""
	ORM object for students stored in the database

	A student uses their associated user object to log in to 
	the app. The Student object holds student specific info for student
	users.
	"""
	__tablename__ = 'students'
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(128), nullable=False)
	last_name = db.Column(db.String(128), nullable=False)

	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # nullable because students could later be associated with a user account
	user = db.relationship("User", backref="user")

	def __init__(self, first_name, last_name, **other_params):
		
		self.first_name = first_name
		self.last_name = last_name
		if ('user_id' in other_params):
			self.user_id = other_params['user_id']

		db.session.add(self)
		db.session.commit()
		log.info('added new student: {} {}'.format(first_name, last_name))
	
	def __repr__(self):
		return "<first_name={} last_name={} user_id={}>".format(self.first_name, self.last_name, self.user_id)

	def delete(self):
		db.session.delete(self)
		db.session.commit()

class StudentsStudentGroupError(Exception):
	pass

class StudentsStudentGroup(db.Model):
	"""
	ORM object for linking table between students and student_groups tables

	A StudentsStudentGroup describes the relationship constraints 
	between a student and a student group for the scheduler. 

	The actual assignment of a student to a student group happens in 
	the Class object.
	"""

	__tablename__ = 'students_student_groups'
	id = db.Column(db.Integer, primary_key=True)
	student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
	student = db.relationship("Student", backref="students_student_groups")
	student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
	student_group = db.relationship("StudentGroup", backref="students_student_groups")
	active = db.Column(db.Boolean, nullable=False, default=True)

	def __init__(self, student_id, student_group_id, **other_params):

		# we want to verify the given id's are actually present in the DB
		if (Course.query.get(student_id) == None):
			raise StudentsStudentGroupError("The student_id {} does not exist in the db".format(student_id))

		from schoolbloc.student_groups.models import StudentGroup
		student_group = StudentGroup.query.get(student_group_id)
		if (student_group == None):
			raise StudentsStudentGroupError("The student_group_id {} does not exist in the db".format(student_group_id))

		self.student_id = student_id
		self.student_group_id = subject_id
		if ('active' in other_params):
			self.active = other_params['active']

		db.session.add(self)
		db.session.commit()
		log.info('acced new StudentsStudentGroup: {} {} <--> {}'.format(student.first_name, 
																		student.last_name, 
																		student_group.name) )
	
	def __repr__(self):
		return "<student_id={} student_group_id={}>".format(self.student_id, self.student_group_id)

	def delete(self):
		db.sesson.delete(self)
		db.session.commit()