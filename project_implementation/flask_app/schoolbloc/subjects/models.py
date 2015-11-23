import logging
from schoolbloc import db

log = logging.getLogger(__name__)

class SubjectError(Exception):
	pass

class Subject(db.Model):
	"""
	ORM object for subjects stored in the database

	A subject is a group of courses
	"""
	__tablename__ = 'subjects'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)

	def __init__(self, name):
		
		self.name = name
		db.session.add(self)
		db.session.commit()
		log.info('added new subject: {}'.format(name))
	
	def __repr__(self):
		return "<name={}>".format(self.name)

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	