"""
This is the script that runs our flask application. This will be
similiar, but slightly different from the production run.py, in
which it will setup logging to go to our emails (optional) and
using redis instead of an in memory dictionary for session
storage
"""
from schoolbloc import app, db
from schoolbloc.scheduler.models import Day
from schoolbloc.users.models import Role, User

if __name__ == '__main__':
    # Set the log level to debug for development
    app.logger.setLevel('INFO')

    # Create the development sqlite databases if they don't already exist
    db.create_all()

    # I'm lazy, just gonna try adding stuff and catching exception if it exists
    try:
        db.session.add(Role(role_type='admin'))
        db.session.add(Role(role_type='teacher'))
        db.session.add(Role(role_type='student'))
        db.session.add(Role(role_type='parent'))
        db.session.add(User(username='admin', password='admin', role_type='admin'))
        db.session.add(Day(name='Monday'))
        db.session.add(Day(name='Tuesday'))
        db.session.add(Day(name='Wednesday'))
        db.session.add(Day(name='Thursday'))
        db.session.add(Day(name='Friday'))
        db.session.commit()
    except:
        db.session.rollback()
