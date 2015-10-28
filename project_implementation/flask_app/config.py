"""
This is where we store configuration details for the flask app.

Checked in here is just some development data that doesn't matter
if it is checked into version control. For the production box, this
file will be different, and need to be kept a secret, as it contains
the secret keys, database passwords, etc.
"""
DEBUG = True
CSRF_ENABLED = False  # We are using javascript web tokens, which migate csrf attacks
SECRET_KEY = 'supersecretkeychangeme'
SQLALCHEMY_DATABASE_URI = 'sqlite:///../schoolbloc.db'
SESSION_KEY_BITS = 128
SESSION_SET_TTL = True
ERROR_404_HELP = False
