import logging
from flask import json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from passlib.hash import pbkdf2_sha512
from schoolbloc import db


log = logging.getLogger(__name__)


class UserError(Exception):
    pass


# TODO figure out how to deal with roles and teachers/admins/students
class Role(db.Model):
    """ Contains the different types of roles that a user could be """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_type = db.Column(db.String(40), nullable=False, unique=True)


class User(db.Model):
    """
    ORM object for users stored in the database.

    This also inherits from UserMixin, which provides every method required
    for flask users to work.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    hashed_passwd = db.Column(db.String, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship("Role", backref="users")

    def __init__(self, username, password, role_type):
        role = Role.query.filter_by(role_type=role_type).one()
        self.username = username
        self.hashed_passwd = pbkdf2_sha512.encrypt(password, rounds=200000, salt_size=16)
        self.role_id = role.id

        try:
            db.session.add(self)
            db.session.commit()
            log.info('added new user: {} <{}>'.format(username, role_type))
        except IntegrityError:
            db.session.rollback()
            raise UserError('The user {} already exists in the database'.format(username))

    def __repr__(self):
        return "<username={} role_id={}>".format(self.username, self.role_id)

    def verify_password(self, password):
        # TODO move to bcrypt, more secure then sha512
        if not pbkdf2_sha512.verify(password, self.hashed_passwd):
            raise UserError('Password does not validate')

    def update_password(self, new_password, commit=True):
        """ Updates the password of this user """
        self.hashed_passwd = pbkdf2_sha512.encrypt(new_password, rounds=200000, salt_size=16)
        if commit:
            db.session.add(self)
            db.session.commit()

    def jsonify(self):
        """ Serialize by converting this object to json """
        return json.dumps({
            'id': self.id,
            'username': self.username,
            'role': self.role.role_type
        })
