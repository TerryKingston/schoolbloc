"""
This is the script that runs our flask application. This will be
similiar, but slightly different from the production run.py, in
which it will setup logging to go to our emails (optional) and
using redis instead of an in memory dictionary for session
storage
"""
from schoolbloc import app, db
from datetime import timedelta
from simplekv.memory import DictStore
from flask_kvsession import KVSessionExtension
from schoolbloc.users.models import Role, User

if __name__ == '__main__':
    # Set the log level to debug for development
    app.logger.setLevel('DEBUG')

    # Create the development sqlite databases if they don't already exist
    db.create_all()

    # I'm lazy, just gonna try adding stuff and catching exception if it exists
    try:
        db.session.add(Role(role_type='admin'))
        db.session.add(Role(role_type='teacher'))
        db.session.add(Role(role_type='student'))
        db.session.add(User(username='admin', password='admin', role_type='admin'))
        db.session.add(User(username='teacher', password='teacher', role_type='teacher'))
        db.session.add(User(username='student', password='student', role_type='student'))
        db.session.commit()
    except:
        pass

    # Create the in memory session manager. In production, this is redis
    store = DictStore()
    app.permanent_session_lifetime = timedelta(hours=1)
    KVSessionExtension(store, app)

    # Run our application
    app.run(host='0.0.0.0', port=5000, use_reloader=True)
