from app import db
from app.models import ActivityLog
from flask_login import current_user
from datetime import datetime

def log_activity(action, target_type=None, details=None):
    """
    Records an action in the database.
    action: 'Login', 'Create', 'Update', 'Delete'
    target_type: 'Instructor', 'Plan', 'User'
    details: 'Created Instructor: Ahmed Ali'
    """
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        log = ActivityLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # لا تفشل العملية الأصلية لو الـ Log فيه مشكلة
        print(f"Logging error: {str(e)}")