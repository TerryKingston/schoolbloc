from schoolbloc.scheduler.models import Notification
from schoolbloc import db
from datetime import datetime

def log_note(type, subject, description):
    created_at = datetime.now()
    db.session.add(Notification(type=type, subject=subject, description=description, created_at=created_at))
    db.session.commit()

    text_color = ""
    if type == 'error':
        text_color = "\033[91m"
    elif type == 'warning':
        text_color = "\033[93m"
    elif type == 'success':
        text_color = "\033[92m"

    print("{}{} : {} - {}\33[0m".format(
           text_color, created_at, type, description))
