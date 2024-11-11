from flask import Blueprint, jsonify, request, session
from database import db
from database.user import User
from database.user_operations import create_user, authenticate_user, update_user_profile
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
                    'name': user.name,
                    'personal_address': {
                        'street': user.personal_street,
                        'city': user.personal_city,
                        'postal_code': user.personal_postal_code,
                        'country': user.personal_country
                    },
                    'billing_address': {
                        'street': user.billing_street,
                        'city': user.billing_city,
                        'postal_code': user.billing_postal_code,
                        'country': user.billing_country
                    },
                    'gdpr_consent': user.gdpr_consent,
                    'gender': user.gender.value if user.gender else None,
                    'age': user.age,
                    'favorite_genres': user.favorite_genres,
                    'referral_source': user.referral_source
                }
            }), 200
    return jsonify({'error': 'Uživatel není přihlášen'}), 401

@bp.route('/api/user/profile', methods=['PUT'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401

    data = request.json
    if not data:
        return jsonify({'error': 'Nebyla poskytnuta žádná data k aktualizaci'}), 400

    # Validace povinných polí pro GDPR
    if 'gdpr_consent' in data and not data['gdpr_consent']:
        return jsonify({'error': 'Pro používání služby je nutný souhlas s GDPR'}), 400

    updated_user = update_user_profile(user_id, data)
    
    if updated_user:
        info_logger.info('Uživatel ID %s aktualizoval svůj profil', user_id)
        return jsonify({
            'message': 'Profil byl úspěšně aktualizován',
            'user': {
                'id': updated_user.id,
                'username': updated_user.username,
                'name': updated_user.name,
                'personal_address': {
                    'street': updated_user.personal_street,
                    'city': updated_user.personal_city,
                    'postal_code': updated_user.personal_postal_code,
                    'country': updated_user.personal_country
                },
                'billing_address': {
                    'street': updated_user.billing_street,
                    'city': updated_user.billing_city,
                    'postal_code': updated_user.billing_postal_code,
                    'country': updated_user.billing_country
                },
                'gdpr_consent': updated_user.gdpr_consent,
                'gender': updated_user.gender.value if updated_user.gender else None,
                'age': updated_user.age,
                'favorite_genres': updated_user.favorite_genres,
                'referral_source': updated_user.referral_source
            }
        }), 200
    
    error_logger.error('Aktualizace profilu uživatele ID %s selhala', user_id)
    return jsonify({'error': 'Aktualizace profilu se nezdařila'}), 400