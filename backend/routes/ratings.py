import logging
from flask import Blueprint, jsonify, request, session
from database import db
from database.rating_operations import add_or_update_rating, get_user_rating

bp = Blueprint('ratings', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/ratings/<isbn>', methods=['POST'])
def rate_book_endpoint(isbn):
    """
    Add or update a user's rating for a specific book.

    This endpoint allows an authenticated user to rate a book by its ISBN.
    Ratings must be integers between 1 and 5.

    Args:
        isbn (str): International Standard Book Number of the book to rate

    Expected JSON payload:
    {
        'rating': 4  # Integer between 1 and 5
    }

    Returns:
    - 200: Rating successfully added or updated
    - 400: Invalid rating or rating addition failed
    - 401: User not authenticated

    Logs:
    - Info log on successful rating
    - Warning log on rating failure
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401

    data = request.json
    rating = data.get('rating')

    if not rating or not isinstance(rating, int) or not (1 <= rating <= 5):
        return jsonify({'error': 'Neplatné hodnocení'}), 400

    success, message = add_or_update_rating(user_id, isbn, rating)

    if success:
        info_logger.info('Uživatel %s ohodnotil knihu %s hodnocením %d', user_id, isbn, rating)
        return jsonify({'message': message}), 200
    else:
        info_logger.warning(
            'Nepodařilo se přidat hodnocení ke knize %s: %s',
            isbn, message
        )
        return jsonify({'error': message}), 400

@bp.route('/api/ratings/<isbn>', methods=['GET'])
def get_user_rating_endpoint(isbn):
    """
    Retrieve the current user's rating for a specific book.

    Fetches the rating given by the authenticated user for a book identified by its ISBN.

    Args:
        isbn (str): International Standard Book Number of the book

    Returns:
    - 200: User's rating successfully retrieved
    - 400: Error retrieving rating
    - 401: User not authenticated

    Response format:
    {
        'rating': 4  # Integer between 1 and 5, or None if no rating exists
    }
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401

    rating, error = get_user_rating(user_id, isbn)

    if error:
        return jsonify({'error': error}), 400

    return jsonify({'rating': rating})
