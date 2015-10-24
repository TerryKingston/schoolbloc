"""
This is a collection of all the models that makeup our database tables that
this blueprint uses. This uses sqlalchemy to allow the benefits of an ORM
as well as letting us be database agnostic.
"""
import logging
from sqlalchemy.exc import IntegrityError
from schoolbloc import db


log = logging.getLogger(__name__)


class ExampleUser(db.Model):
    """
    Very basic example of this. It can do much more, such as querying and
    deleting rows, creating relationships between different tables, creating
    indexes on columns, etc.
    """
    __tablename__ = 'example_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    phone = db.Column(db.String(10), nullable=True, default=None)
    active = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, name, phone=None, active=True):
        """ An example of initializing and save data into this table """
        self.name = name
        self.phone = phone
        self.active = active

        # Attempt to save it into the database. Rollback and log the error if that
        # fails for any reason (such as a unique constraint being violated or a
        # connection error with the underlying database.
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Exception("A unique constraint was violated trying to add this user")
        except Exception as e:
            log.exception(e)
            raise Exception("Failed to add user to database")

    def do_something_with_data(self):
        """ An example of accessing the data in the database """
        return "{} just did something with the database".format(self.name)
