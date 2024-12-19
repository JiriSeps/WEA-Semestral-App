from flask import Blueprint, request, jsonify
from database.audit import AuditLog, AuditEventType
from database import db

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/api/audit_logs', methods=['GET'])
def get_audit_logs():
    try:
        # Query parameters
        date_filter = request.args.get('date')  # Expected format: YYYY-MM-DD
        event_type_filter = request.args.get('event_type')  # Example: "user_login"
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)

        # Base query
        query = AuditLog.query

        # Apply filters
        if date_filter:
            from datetime import datetime
            try:
                date_start = datetime.strptime(date_filter, "%Y-%m-%d")
                date_end = date_start.replace(hour=23, minute=59, second=59)
                query = query.filter(AuditLog.timestamp.between(date_start, date_end))
            except ValueError:
                return jsonify({'error': 'Invalid date format, expected YYYY-MM-DD'}), 400

        if event_type_filter:
            try:
                event_type = AuditEventType(event_type_filter)
                query = query.filter(AuditLog.event_type == event_type)
            except ValueError:
                return jsonify({'error': 'Invalid event type'}), 400

        # Apply pagination and sorting
        query = query.order_by(AuditLog.timestamp.desc())
        paginated_logs = query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize results
        logs = [
            {
                'id': log.id,
                'event_type': log.event_type.value,
                'timestamp': log.timestamp.isoformat(),
                'username': log.username,
                'book_isbn': log.book_isbn,
                'additional_data': log.additional_data
            }
            for log in paginated_logs.items
        ]

        return jsonify({
            'logs': logs,
            'total_logs': paginated_logs.total,
            'page': paginated_logs.page,
            'per_page': paginated_logs.per_page,
            'total_pages': paginated_logs.pages
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch audit logs: {str(e)}'}), 500
