from flask import Blueprint, jsonify, request, session
from database import db
from database.cart_operations import toggle_cart, get_user_shopping_cart, is_book_in_shopping_cart
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
    
    books, total, error = get_user_shopping_cart(user_id, page, per_page)
    
    if books is None:
        error_logger.error('Chyba při získávání knih v košíku: %s', error)
        return jsonify({'error': error}), 400
        
    # Filter out books where is_visible is False
    filtered_books = [book for book in books if book['is_visible']]
    
    books_data = [{
        'ISBN10': book['book'].ISBN10,
        'ISBN13': book['book'].ISBN13,
        'Title': book['book'].Title,
        'Author': book['book'].Author,
        'Genres': book['book'].Genres,
        'Cover_Image': book['book'].Cover_Image,
        'Description': book['book'].Description,
        'Year_of_Publication': book['book'].Year_of_Publication,
        'Number_of_Pages': book['book'].Number_of_Pages,
        'Average_Rating': book['book'].Average_Rating,
        'Number_of_Ratings': book['book'].Number_of_Ratings,
        'Price': book['book'].Price,
        'is_visible': book['is_visible']
    } for book in filtered_books]
    
    return jsonify({
        'books': books_data,
        'total_books': len(filtered_books),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(filtered_books) + per_page - 1) // per_page
    })

@bp.route('/api/shoppingcart/<isbn>', methods=['POST'])
def toggle_cart_book_endpoint(isbn):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    success, message = toggle_cart(user_id, isbn)
    
    if success:
        info_logger.info('Změněn stav knihy v košíku %s pro uživatele %s', isbn, user_id)
        return jsonify({
            'message': message,
            'is_in_cart': is_book_in_shopping_cart(user_id, isbn)[0]
        }), 200
    else:
        info_logger.warning(
            'Nepodařilo se změnit stav knihy v košíku %s: %s',
            isbn, message
        )
        return jsonify({'error': message}), 400

@bp.route('/api/shoppingcart/<isbn>/status', methods=['GET'])
def check_cart_status_endpoint(isbn):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    is_in_cart, error = is_book_in_shopping_cart(user_id, isbn)
    
    if error:
        info_logger.warning(
            'Nepodařilo se zjistit stav knihy v košíku %s: %s',
            isbn, error
        )
        return jsonify({'error': error}), 400
        
    return jsonify({'is_in_cart': is_in_cart})