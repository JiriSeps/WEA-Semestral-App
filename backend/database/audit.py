# models/audit.py
from enum import Enum
from datetime import datetime
from . import db

class AuditEventType(Enum):
    """
    Enumeration of audit event types for tracking system activities.

    This enum categorizes different types of events that can be logged in the system,
    divided into user-related and book-related events.

    User Events:
    - USER_REGISTER: When a new user registers in the system
    - USER_LOGIN: When a user logs into the system
    - USER_LOGOUT: When a user logs out of the system

    Book Events:
    - BOOK_HIDE: When a book is hidden from public view
    - BOOK_SHOW: When a book is made visible
    - BOOK_ADD: When a new book is added to the system
    """

    USER_REGISTER = 'user_register'
    USER_LOGIN = 'user_login'
    USER_LOGOUT = 'user_logout'

    BOOK_HIDE = 'book_hide'
    BOOK_SHOW = 'book_show'
    BOOK_ADD = 'book_add'

class AuditLog(db.Model):
    """
    Database model representing an audit log entry for tracking system events.

    This model captures detailed information about various system activities,
    providing a comprehensive audit trail for tracking user and book-related actions.

    Attributes:
        id (int): Primary key for the audit log entry.
        event_type (AuditEventType): The type of event that occurred.
        timestamp (datetime): The exact time when the event was recorded (defaults to current UTC time).
        username (str): The username of the user who performed the action.
        book_isbn (str, optional): ISBN of the book related to the event (if applicable).
        book (Book, optional): Relationship to the associated book object.
        additional_data (dict, optional): JSON field for storing extra event-specific information.

    Example:
        audit_entry = AuditLog(
            event_type=AuditEventType.USER_LOGIN,
            username='john_doe',
            additional_data={'ip_address': '192.168.1.1'}
        )
        db.session.add(audit_entry)
        db.session.commit()
    """
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.Enum(AuditEventType), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    username = db.Column(db.String(80), nullable=False)

    # Foreign key na knihu
    book_isbn = db.Column(db.String(10), db.ForeignKey('book.ISBN10'), nullable=True)
    # Relationship pro snadnější přístup k datům knihy
    book = db.relationship('Book', backref=db.backref('audit_logs', lazy=True))

    # Pro další informace
    additional_data = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<AuditLog {self.event_type.value} by {self.username} at {self.timestamp}>'
