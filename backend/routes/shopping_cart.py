import logging
from flask import Blueprint, jsonify, request, session
from database.cart_operations import (
    toggle_cart,
    get_formatted_shopping_cart,
    is_book_in_shopping_cart,
    clear_shopping_cart
)

bp = Blueprint('shopping_cart', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/shoppingcart', methods=['GET'])
def get_cart_books_endpoint():
    """
    Retrieve paginated list of books in the shopping cart.

    Fetches books from the shopping cart with optional pagination.

    Query Parameters:
    - page (int, optional): Page number for pagination. Defaults to 1.
    - per_page (int, optional): Number of items per page. Defaults to 25.

    Returns:
    - 200: Successfully retrieved cart books
    - 401: Error retrieving cart books

    Response format:
    {
        'books': [
            {
                # Book details
            }
        ],
        'total_books': int,
        'page': int,
        'per_page': int
    }
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    result = get_formatted_shopping_cart(page, per_page)

    if result.get('error'):
        error_logger.error('Chyba při získávání knih v košíku: %s', result['error'])
        return jsonify({'error': result['error']}), 401

    return jsonify(result)

@bp.route('/api/shoppingcart/<isbn>', methods=['POST'])
def toggle_cart_book_endpoint(isbn):
    """
    Toggle a book's presence in the shopping cart.

    Adds the book to the cart if it's not present, or removes it if it is.

    Args:
        isbn (str): International Standard Book Number of the book

    Returns:
    - 200: Successfully toggled book in cart
    - 401: Error toggling book in cart

    Response format:
    {
        'in_cart': bool,  # Current cart status of the book
        'message': str    # Description of the action taken
    }
    """
    result = toggle_cart(isbn)

    if result.get('error'):
        info_logger.warning(
            'Nepodařilo se změnit stav knihy v košíku %s: %s',
            isbn, result['error']
        )
        return jsonify({'error': result['error']}), 401

    info_logger.info('Změněn stav knihy v košíku %s', isbn)
    return jsonify(result), 200

@bp.route('/api/shoppingcart/<isbn>/status', methods=['GET'])
def check_cart_status_endpoint(isbn):
    """
    Check if a specific book is in the shopping cart.

    Args:
        isbn (str): International Standard Book Number of the book

    Returns:
    - 200: Successfully retrieved book cart status
    - 400: Error checking book cart status

    Response format:
    {
        'in_cart': bool  # Whether the book is currently in the cart
    }
    """
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
    """
    Clear all items from the shopping cart.

    Removes all books currently in the shopping cart.

    Returns:
    - 200: Shopping cart successfully cleared
    - 400: Error clearing the cart
    - 500: Unexpected error during cart clearing

    Response format:
    {
        'message': 'Košík byl úspěšně vyprázdněn'  # Success message
    }
    """
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
