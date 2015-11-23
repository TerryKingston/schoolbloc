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