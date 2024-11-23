from flask import Blueprint, jsonify, request, session
from database.cart_operations import (
    toggle_cart,
    get_formatted_shopping_cart,
    is_book_in_shopping_cart
)
import logging

bp = Blueprint('shopping_cart', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/shoppingcart', methods=['GET'])
def get_cart_books_endpoint():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    
    result = get_formatted_shopping_cart(user_id, page, per_page)
    
    if result.get('error'):
        error_logger.error('Chyba při získávání knih v košíku: %s', result['error'])
        return jsonify({'error': result['error']}), 400
        
    return jsonify(result)

@bp.route('/api/shoppingcart/<isbn>', methods=['POST'])
def toggle_cart_book_endpoint(isbn):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    result = toggle_cart(user_id, isbn)
    
    if result.get('error'):
        info_logger.warning(
            'Nepodařilo se změnit stav knihy v košíku %s: %s',
            isbn, result['error']
        )
        return jsonify({'error': result['error']}), 400
    
    info_logger.info('Změněn stav knihy v košíku %s pro uživatele %s', isbn, user_id)
    return jsonify(result), 200

@bp.route('/api/shoppingcart/<isbn>/status', methods=['GET'])
def check_cart_status_endpoint(isbn):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    result = is_book_in_shopping_cart(user_id, isbn)
    
    if result.get('error'):
        info_logger.warning(
            'Nepodařilo se zjistit stav knihy v košíku %s: %s',
            isbn, result['error']
        )
        return jsonify({'error': result['error']}), 400
        
    return jsonify(result)