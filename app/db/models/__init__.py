# app/db/models/__init__.py
from app.db.models.notification_log import NotificationLog
from app.db.models.scholarship import Scholarship
from app.db.models.scholarship_source import ScholarshipSource
from app.db.models.user import User
from app.db.models.user_filter import UserFilter

__all__ = ["User", "UserFilter", "ScholarshipSource", "Scholarship", "NotificationLog"]