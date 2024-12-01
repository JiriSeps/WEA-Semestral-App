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
import logging

bp = Blueprint('users', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/register', methods=['POST'])
def register():
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
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    result = get_formatted_user_data(user_id)
    
    if result.get('error'):
        return jsonify({'error': result['error']}), 400
        
    return jsonify(result), 200

@bp.route('/api/user/profile', methods=['PUT'])
def update_profile():
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