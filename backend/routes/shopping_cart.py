from flask import Blueprint, jsonify, request, session
from database.cart_operations import (
    toggle_cart,
    get_formatted_shopping_cart,
    is_book_in_shopping_cart,
    clear_shopping_cart
)
import logging

bp = Blueprint('shopping_cart', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/shoppingcart', methods=['GET'])
def get_cart_books_endpoint():
    # No need for user_id anymore, we use session directly
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    
    result = get_formatted_shopping_cart(page, per_page)
    
    if result.get('error'):
        error_logger.error('Chyba při získávání knih v košíku: %s', result['error'])
        return jsonify({'error': result['error']}), 400
        
    return jsonify(result)

@bp.route('/api/shoppingcart/<isbn>', methods=['POST'])
def toggle_cart_book_endpoint(isbn):
    # No need for user_id anymore, we use session directly
    result = toggle_cart(isbn)
    
    if result.get('error'):
        info_logger.warning(
            'Nepodařilo se změnit stav knihy v košíku %s: %s',
            isbn, result['error']
        )
        return jsonify({'error': result['error']}), 400
    
    info_logger.info('Změněn stav knihy v košíku %s', isbn)
    return jsonify(result), 200

@bp.route('/api/shoppingcart/<isbn>/status', methods=['GET'])
def check_cart_status_endpoint(isbn):
    # No need for user_id anymore, we use session directly
    result = is_book_in_shopping_cart(isbn)
    
    if result.get('error'):
        info_logger.warning(
            'Nepodařilo se zjistit stav knihy v košíku %s: %s',
            isbn, result['error']
        )
        return jsonify({'error': result['error']}), 400
        
    return jsonify(result)

@bp.route('/api/shoppingcart', methods=['DELETE'])
def clear_cart_endpoint():
    """Endpoint pro vymazání celého košíku"""
    try:
        result = clear_shopping_cart()
        
        if result.get('error'):
            error_logger.error('Chyba při mazání košíku: %s', result['error'])
            return jsonify({'error': result['error']}), 400
            
        info_logger.info('Košík byl úspěšně vyprázdněn')
        return jsonify({'message': 'Košík byl úspěšně vyprázdněn'}), 200
        
    except Exception as e:
        error_logger.error('Neočekávaná chyba při mazání košíku: %s', str(e))
        return jsonify({'error': 'Neočekávaná chyba při mazání košíku'}), 500