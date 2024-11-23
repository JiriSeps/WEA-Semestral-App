from flask import Blueprint, jsonify, request, session
from database.favorite_operations import (
    toggle_favorite,
    get_formatted_favorite_books,
    is_book_favorite
)
import logging

bp = Blueprint('favorites', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/favorites', methods=['GET'])
def get_favorite_books_endpoint():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    
    result = get_formatted_favorite_books(user_id, page, per_page)
    
    if result.get('error'):
        error_logger.error('Chyba při získávání oblíbených knih: %s', result['error'])
        return jsonify({'error': result['error']}), 400
        
    return jsonify(result)

@bp.route('/api/favorites/<isbn>', methods=['POST'])
def toggle_favorite_book_endpoint(isbn):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    success, message = toggle_favorite(user_id, isbn)
    
    if success:
        info_logger.info('Změněn stav oblíbené knihy %s pro uživatele %s', isbn, user_id)
        return jsonify({'message': message}), 200
    else:
        info_logger.warning(
            'Nepodařilo se změnit stav oblíbené knihy %s: %s',
            isbn, message
        )
        return jsonify({'error': message}), 400

@bp.route('/api/favorites/<isbn>/status', methods=['GET'])
def check_favorite_status_endpoint(isbn):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    is_favorite, error = is_book_favorite(user_id, isbn)
    
    if error:
        info_logger.warning(
            'Nepodařilo se zjistit stav oblíbené knihy %s: %s',
            isbn, error
        )
        return jsonify({'error': error}), 400
        
    return jsonify({'is_favorite': is_favorite})