# models/audit.py
from enum import Enum
from datetime import datetime
from . import db

class AuditEventType(Enum):
    # Uživatelské události
    USER_REGISTER = 'user_register'
    USER_LOGIN = 'user_login'
    USER_LOGOUT = 'user_logout'
    
    # CDB události
    BOOK_HIDE = 'book_hide'
    BOOK_SHOW = 'book_show'
    BOOK_ADD = 'book_add'

class AuditLog(db.Model):
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