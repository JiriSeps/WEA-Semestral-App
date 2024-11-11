from flask import Blueprint, jsonify, request, session
from database import db
from database.user import User
from database.user_operations import create_user, authenticate_user
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

    user = create_user(username, password, name)
    if user:
        info_logger.info('Nový uživatel %s byl registrován', username)
        return jsonify({'message': 'Uživatel úspěšně zaregistrován'}), 201
    info_logger.warning('Registrace uživatele %s selhala', username)
    return jsonify({'error': 'Registrace se nezdařila'}), 400

@bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Uživatelské jméno a heslo jsou povinné'}), 400

    user = authenticate_user(username, password)
    if user:
        session['user_id'] = user.id
        info_logger.info('Uživatel %s se přihlásil', username)
        return jsonify({
            'message': 'Přihlášení úspěšné',
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name
            }
        }), 200
    info_logger.warning('Nepodařilo se přihlásit uživatele %s', username)
    return jsonify({'error': 'Neplatné přihlašovací údaje'}), 401

@bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Odhlášení úspěšné'}), 200

@bp.route('/api/user', methods=['GET'])
def get_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name
                }
            }), 200
    return jsonify({'error': 'Uživatel není přihlášen'}), 401