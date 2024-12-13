import logging
from flask import Blueprint, jsonify, request, session
from database.comment_operations import (
    add_comment,
    get_comments_for_book,
    delete_comment,
    get_formatted_comments_for_book
)

bp = Blueprint('comments', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/comments/<isbn>', methods=['GET'])
def get_book_comments_endpoint(isbn):
    """
    Retrieve paginated comments for a specific book.

    URL Parameters:
    - isbn (str): International Standard Book Number of the book

    Query Parameters:
    - page (int, optional): Page number for pagination. Defaults to 1.
    - per_page (int, optional): Number of comments per page. Defaults to 10.

    Returns:
    JSON object containing:
    - comments: List of formatted comments for the book
    - total_comments: Total number of comments
    - page: Current page number
    - per_page: Number of comments per page
    - total_pages: Total number of pages

    Raises:
    404 Not Found if there's an issue retrieving comments for the book
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    result = get_formatted_comments_for_book(isbn, page, per_page)

    if result.get('error'):
        info_logger.warning(result['error'])
        return jsonify({'error': result['error']}), 404

    info_logger.info('Úspěšně získány komentáře pro knihu %s', isbn)
    return jsonify(result)

@bp.route('/api/comments', methods=['POST'])
def add_book_comment_endpoint():
    """
    Add a new comment to a book.

    Requires user authentication.

    Request JSON Body:
    - book_isbn (str): ISBN of the book being commented on
    - text (str): Text content of the comment

    Returns:
    - 201 Created: Successfully added comment
        JSON: {'message': 'Komentář byl přidán'}
    - 400 Bad Request: Missing required data or comment creation failed
        JSON: {'error': 'Chybí povinné údaje' or specific error message}
    - 401 Unauthorized: User not logged in

    Raises:
    Logs warnings for failed comment additions
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401

    data = request.json
    book_isbn = data.get('book_isbn')
    text = data.get('text')

    if not book_isbn or not text:
        return jsonify({'error': 'Chybí povinné údaje'}), 400

    success, message = add_comment(book_isbn, user_id, text)

    if success:
        info_logger.info('Uživatel %s přidal komentář ke knize %s', user_id, book_isbn)
        return jsonify({'message': message}), 201
    else:
        info_logger.warning(
            'Nepodařilo se přidat komentář ke knize %s: %s',
            book_isbn, message
        )
        return jsonify({'error': message}), 400

@bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_book_comment_endpoint(comment_id):
    """
    Delete a specific comment.

    Requires user authentication.
    Users can only delete their own comments.

    URL Parameters:
    - comment_id (int): Unique identifier of the comment to be deleted

    Returns:
    - 200 OK: Successfully deleted comment
        JSON: {'message': 'Komentář byl smazán'}
    - 400 Bad Request: Comment deletion failed
        JSON: {'error': specific error message}
    - 401 Unauthorized: User not logged in

    Raises:
    Logs warnings for failed comment deletions
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401

    success, message = delete_comment(comment_id, user_id)

    if success:
        info_logger.info('Komentář %s byl smazán uživatelem %s', comment_id, user_id)
        return jsonify({'message': message}), 200
    else:
        info_logger.warning(
            'Nepodařilo se smazat komentář %s: %s',
            comment_id, message
        )
        return jsonify({'error': message}), 400
