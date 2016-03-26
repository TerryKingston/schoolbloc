from schoolbloc.scheduler.models import Notification
from schoolbloc import db
from datetime import datetime

def log_note(type, subject, description):
    db.session.add(Notification(type=type, subject=subject, description=description, created_at=datetime.now()))
    db.session.commit()