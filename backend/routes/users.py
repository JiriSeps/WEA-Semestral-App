import logging
from flask import Blueprint, jsonify, request, session
from database.user_operations import (
    authenticate_user,
    create_user,
    update_user_profile,
    get_user_profile,
    get_formatted_user_data
)
from database.audit import AuditEventType
from database.audit_operations import create_audit_log

bp = Blueprint('users', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/register', methods=['POST'])
def register():
    """
    Handle user registration endpoint.

    Expected JSON payload:
    - username (str): Desired username for the new user
    - password (str): User's password
    - name (str): User's full name

    Returns:
    - 201 status with user registration details on success
    - 400 status with error message if registration fails
    
    Logs registration attempt and creates an audit log entry.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')

    if not username or not password or not name:
        return jsonify({'error': 'Všechna pole jsou povinná'}), 400

    result = create_user(username, password, name)

    if result.get('error'):
        info_logger.warning('Registrace uživatele %s selhala', username)
        return jsonify({'error': result['error']}), 400

    create_audit_log(
        event_type=AuditEventType.USER_REGISTER,
        username=username,
        additional_data={'name': name}
    )

    info_logger.info('Nový uživatel %s byl registrován', username)
    return jsonify(result), 201

@bp.route('/api/login', methods=['POST'])
def login():
    """
    Handle user login endpoint.

    Expected JSON payload:
    - username (str): User's username
    - password (str): User's password

    Returns:
    - 200 status with user details on successful authentication
    - 401 status with error message if authentication fails
    
    Creates a user session and logs the login event.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Uživatelské jméno a heslo jsou povinné'}), 400

    result = authenticate_user(username, password)

    if result.get('error'):
        return jsonify({'error': result['error']}), 401

    session['user_id'] = result['user']['id']
    create_audit_log(
        event_type=AuditEventType.USER_LOGIN,
        username=username
    )

    info_logger.info('Uživatel %s se přihlásil', username)
    return jsonify(result), 200

@bp.route('/api/logout', methods=['POST'])
def logout():
    """
    Handle user logout endpoint.

    Performs the following actions:
    - Retrieves the current user from the session
    - Creates an audit log entry for the logout event
    - Clears the user session

    Returns:
    - 200 status with success message on logout
    """
    user_id = session.get('user_id')
    if user_id:
        user = get_user_profile(user_id)
        if user and not user.get('error'):
            create_audit_log(
                event_type=AuditEventType.USER_LOGOUT,
                username=user['username']
            )
            info_logger.info('Uživatel %s se odhlásil', user['username'])

    session.pop('user_id', None)
    return jsonify({'message': 'Odhlášení úspěšné'}), 200

@bp.route('/api/user', methods=['GET'])
def get_user():
    """
    Retrieve current user's profile information.

    Requires an active user session.

    Returns:
    - 200 status with formatted user data on success
    - 401 status if no user is logged in
    - 400 status if there's an error retrieving user data
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401

    result = get_formatted_user_data(user_id)

    if result.get('error'):
        return jsonify({'error': result['error']}), 400

    return jsonify(result), 200

@bp.route('/api/user/profile', methods=['PUT'])
def update_profile():
    """
    Update the current user's profile information.

    Requires an active user session.

    Expected JSON payload:
    - Dictionary containing profile fields to update

    Returns:
    - 200 status with updated user data on success
    - 401 status if no user is logged in
    - 400 status if no update data provided or update fails
    
    Logs profile update attempts and creates an audit log entry.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401

    data = request.json
    if not data:
        return jsonify({'error': 'Nebyla poskytnuta žádná data k aktualizaci'}), 400

    result = update_user_profile(user_id, data)

    if result.get('error'):
        error_logger.error('Aktualizace profilu uživatele ID %s selhala', user_id)
        return jsonify({'error': result['error']}), 400

    info_logger.info('Uživatel ID %s aktualizoval svůj profil', user_id)
    return jsonify(result), 200
