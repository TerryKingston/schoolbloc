import logging
from sqlalchemy.exc import IntegrityError
from schoolbloc import db

log = logging.getLogger(__name__)

class ClassroomError(Exception):
	pass

class Classroom(db.Model):
	"""
	ORM object for classrooms stored in the database

	A classroom object represents a physical classroom in
	a school building.
	"""

	__tablename__ = 'classrooms'
	id = db.Column(db.Integer, primary_key=True)
	room_number = db.Column(db.Integer, nullable=False, unique=True) # the user assigned room number
	max_student_count = db.Column(db.Integer)

	def __init__(self, room_number, **other_params):

		self.room_number = room_number
		if ('max_student_count' in other_params):
			self.max_student_count = other_params['max_student_count']

		# the room number could be a duplicate
		try: 
			db.session.add(self)
			db.session.commit()
			log.info('added new classroom: {}'.format(room_number))
		except IntegrityError:
			db.session.rollback()
			raise ClassroomError("The room number {} already exists in the db".format(room_number))

	def __repr__(self):
		return "<room_number={} max_student_count={}>".format(self.room_number, self.max_student_count)

	def delete(self):
		db.session.delete(self)
		db.session.commit()

class ClassroomsTeacher(db.Model):
	"""
	ORM object for linking table between classrooms and teachers tables

	A ClassroomsTeacher describes the relationship constraints 
	between a classroom and a teacher for the scheduler. 

	The actual assignment of a classroom to a teacher happens in 
	the Class object.
	"""

	__tablename__ = 'classrooms_teachers'
	id = db.Column(db.Integer, primary_key=True)
	