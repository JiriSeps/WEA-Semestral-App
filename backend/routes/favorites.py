import logging
from flask import Blueprint, jsonify, request, session
from database.favorite_operations import (
    toggle_favorite,
    get_formatted_favorite_books,
    is_book_favorite
)

bp = Blueprint('favorites', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/favorites', methods=['GET'])
def get_favorite_books_endpoint():
    """
    Retrieve a paginated list of user's favorite books.

    Requires user authentication.

    Query Parameters:
    - page (int, optional): Page number for pagination. Defaults to 1.
    - per_page (int, optional): Number of books per page. Defaults to 25.

    Returns:
    JSON object containing:
    - books: List of user's favorite books
    - total_books: Total number of favorite books
    - page: Current page number
    - per_page: Number of books per page
    - total_pages: Total number of pages

    Raises:
    401 Unauthorized: User not logged in
    400 Bad Request: Error retrieving favorite books
    """
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
    """
    Toggle the favorite status of a book for the current user.

    Requires user authentication.

    URL Parameters:
    - isbn (str): International Standard Book Number of the book

    Returns:
    - 200 OK: Successfully toggled favorite status
        JSON: {'message': 'Kniha přidána/odebrána z oblíbených'}
    - 400 Bad Request: Failed to toggle favorite status
        JSON: {'error': specific error message}
    - 401 Unauthorized: User not logged in

    Behavior:
    - If the book is not a favorite, it will be added to favorites
    - If the book is already a favorite, it will be removed from favorites
    """
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
    """
    Check if a specific book is in the user's favorites.

    Requires user authentication.

    URL Parameters:
    - isbn (str): International Standard Book Number of the book

    Returns:
    - 200 OK: Successfully retrieved favorite status
        JSON: {'is_favorite': boolean}
    - 400 Bad Request: Failed to retrieve favorite status
        JSON: {'error': specific error message}
    - 401 Unauthorized: User not logged in

    Response:
    - is_favorite (bool): True if the book is in user's favorites, False otherwise
    """
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
