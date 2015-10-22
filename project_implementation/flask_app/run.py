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

if __name__ == '__main__':
    # Set the log level to debug for development
    app.logger.setLevel('DEBUG')

    # Create the development sqlite databases if they don't already exist
    db.create_all()

    # Create the in memory session manager. In production, this is redis
    store = DictStore()
    app.permanent_session_lifetime = timedelta(hours=1)
    KVSessionExtension(store, app)

    # Run our application
    app.run(host='0.0.0.0', port=5000, use_reloader=True)
