import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from passlib.hash import pbkdf2_sha512
from schoolbloc import db


log = logging.getLogger(__name__)


class RoleError(Exception):
    pass


class UserError(Exception):
    pass


# TODO somewhere else we will want to create default roles (setup.py or something?)
class Role(db.Model):
    """ Contains the different types of roles that a user could be """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_type = db.Column(db.String(40), nullable=False, unique=True)
    # Has a users backref via Users relationship

    def __init__(self, role_type):
        self.role_type = role_type
        try:
            db.session.add(self)
            db.session.commit()
            log.info('added new role: {}'.format(role_type))
        except IntegrityError:
            db.session.rollback()
            raise RoleError("The role {} already exists in the db".format(role_type))

    def __repr__(self):
        return "<role id={} role_type={}>".format(self.id, self.role_type)

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# TODO setup flask-login stuff with this object
class User(db.Model):
    """ Object for user database fields, as well as flask-login functionality """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    hashed_passwd = db.Column(db.String, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship("Role", backref="users")

    def __init__(self, username, password, role_type):
        try:
            role = Role.query.filter_by(role_type=role_type).one()
        except NoResultFound:
            raise RoleError('The role {} does not exist'.format(role_type))

        self.username = username
        self.hashed_passwd = pbkdf2_sha512.encrypt(password, rounds=200000, salt_size=16)
        self.role_id = role.id

        try:
            db.session.add(self)
            db.session.commit()
            log.info('added new user: {} <{}>'.format(username, role_type))
        except IntegrityError as e:
            db.session.rollback()
            raise UserError('The user {} already exists in the database'.format(username))

    def __repr__(self):
        return "<username={} role_id={}>".format(self.username, self.role_id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def verify_password(self, password):
        return pbkdf2_sha512.verify(password, self.hashed_passwd)
