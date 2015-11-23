import logging
from schoolbloc import db

log = logging.getLogger(__name__)

class TeacherError(Exception):
	pass

class Teacher(db.Model):
	"""
	ORM object for teachers stored in the database

	A teacher uses their associated user object to log in to the app.
	The teacher object holds teacher specific info for teacher users.
	"""

	__tablename__ = 'teachers'
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(128), nullable=False)
	last_name = db.Column(db.String(128), nullable=False)

	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # nullable because the teacher could later be associated with a user account
	user = db.relationship("User", backref="user")

	def __init__(self, first_name, last_name, **other_params):

		self.first_name = first_name
		self.last_name = last_name
		if ('user_id' in other_params):
			self.user_id = other_params['user_id']

		db.session.add(self)
		db.session.commit()
		log.info('added new teacher: {} {}'.format(first_name, last_name))

	def __repr__(self):
		return "<first_name={} last_name={} user_id={}>".format(self.first_name, self.last_name, self.user_id)

	def delete(self):
		db.session.delete(self)
		db.session.commit()