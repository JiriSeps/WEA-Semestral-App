from flask import Blueprint, jsonify, request, session
from database import db
from database.favorite_operations import toggle_favorite, get_user_favorite_books, is_book_favorite
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
    
    books, total, error = get_user_favorite_books(user_id, page, per_page)
    
    if books is None:
        error_logger.error('Chyba při získávání oblíbených knih: %s', error)
        return jsonify({'error': error}), 400
        
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
        'is_visible': book['is_visible']
    } for book in books]
    
    return jsonify({
        'books': books_data,
        'total_books': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

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