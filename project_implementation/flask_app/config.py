"""
This is where we store configuration details for the flask app.

Checked in here is just some development data that doesn't matter
if it is checked into version control. For the production box, this
file will be different, and need to be kept a secret, as it contains
the secret keys, database passwords, etc.
"""
from datetime import timedelta

DEBUG = True
SECRET_KEY = 'supersecretkeychangeme'
SQLALCHEMY_DATABASE_URI = 'sqlite:///../schoolbloc.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
TMP_FOLDER = '///../tmp/'
SESSION_KEY_BITS = 128
SESSION_SET_TTL = True
ERROR_404_HELP = False
JWT_EXPIRATION_DELTA = timedelta(hours=24)
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['csv'])
