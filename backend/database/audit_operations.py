from database.audit import db, AuditLog, AuditEventType
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

def create_audit_log(event_type: AuditEventType, username: str, book_isbn: str = None, 
                    additional_data: dict = None) -> tuple[bool, str]:
    """
    Vytvoří nový auditní záznam.
    """
    try:
        new_audit = AuditLog(
            event_type=event_type,
            username=username,
            book_isbn=book_isbn,  # Už nepotřebujeme book_title
            additional_data=additional_data,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_audit)
        db.session.commit()
        return True, "Audit log created successfully"
    except SQLAlchemyError as e:
        db.session.rollback()
        return False, str(e)

def get_audit_logs(page: int = 1, per_page: int = 50) -> tuple[list, int, str]:
    """
    Získá auditní záznamy s stránkováním.
    """
    try:
        paginated_logs = AuditLog.query\
            .order_by(AuditLog.timestamp.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return paginated_logs.items, paginated_logs.total, "Success"
    except SQLAlchemyError as e:
        return None, 0, str(e)

def get_user_audit_logs(username: str, page: int = 1, per_page: int = 50) -> tuple[list, int, str]:
    """
    Získá auditní záznamy pro konkrétního uživatele.
    """
    try:
        paginated_logs = AuditLog.query\
            .filter_by(username=username)\
            .order_by(AuditLog.timestamp.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return paginated_logs.items, paginated_logs.total, "Success"
    except SQLAlchemyError as e:
        return None, 0, str(e)

def get_book_audit_logs(book_isbn: str) -> tuple[list, str]:
    """
    Získá auditní záznamy pro konkrétní knihu.
    """
    try:
        logs = AuditLog.query\
            .filter_by(book_isbn=book_isbn)\
            .order_by(AuditLog.timestamp.desc())\
            .all()
        return logs, "Success"
    except SQLAlchemyError as e:
        return None, str(e)

def get_event_type_logs(event_type: AuditEventType, page: int = 1, 
                       per_page: int = 50) -> tuple[list, int, str]:
    """
    Získá auditní záznamy pro konkrétní typ události.
    """
    try:
        paginated_logs = AuditLog.query\
            .filter_by(event_type=event_type)\
            .order_by(AuditLog.timestamp.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return paginated_logs.items, paginated_logs.total, "Success"
    except SQLAlchemyError as e:
        return None, 0, str(e)

def get_recent_audit_logs(limit: int = 10) -> tuple[list, str]:
    """
    Získá nejnovější auditní záznamy.
    """
    try:
        logs = AuditLog.query\
            .order_by(AuditLog.timestamp.desc())\
            .limit(limit)\
            .all()
        return logs, "Success"
    except SQLAlchemyError as e:
        return None, str(e)