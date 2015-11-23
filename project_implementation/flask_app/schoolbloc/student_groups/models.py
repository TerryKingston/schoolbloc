import logging
from schoolbloc import db

log = logging.getLogger(__name__)

class StudentGroupError(Exception):
	pass

class StudentGroup(db.Model):
	"""
	ORM object for student groups stored in the database

	A Collection of students
	"""
	__tablename__ = 'student_groups'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), nullable=False)

	def __init__(self, name):
		
		self.name = name

		db.session.add(self)
		db.session.commit()
		log.info('added new student group: {}'.format(name))
	
	def __repr__(self):
		return "<name={}>".format(self.name)

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	