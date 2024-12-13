import logging
from flask import Blueprint, jsonify, request, session
from database.book_operations import (
    search_books,
    get_book_by_isbn,
    get_all_unique_genres,
    fetch_and_update_books,
    get_favorite_books
)

bp = Blueprint('books', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/books')
def get_books():
    """
    Retrieve a paginated list of books based on search criteria.

    Query Parameters:
    - page (int, optional): Page number for pagination. Defaults to 1.
    - per_page (int, optional): Number of books per page. Defaults to 25.
    - title (str, optional): Filter books by title (partial match).
    - author (str, optional): Filter books by author (partial match).
    - isbn (str, optional): Filter books by ISBN (partial match).
    - genres (str, optional): Filter books by genres (comma-separated).
    - favorites (str, optional): If 'true', retrieves user's favorite books.

    Returns:
    JSON object containing:
    - books: List of book data matching the search criteria
    - total_books: Total number of books matching the search
    - page: Current page number
    - per_page: Number of books per page
    - total_pages: Total number of pages

    Raises:
    500 Internal Server Error if there's an issue retrieving books
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    title_query = request.args.get('title', '')
    author_query = request.args.get('author', '')
    isbn_query = request.args.get('isbn', '')
    genres_query = request.args.get('genres', '')
    show_favorites = request.args.get('favorites', '').lower() == 'true'
    user_id = session.get('user_id')

    try:
        if show_favorites and user_id:
            books_data, total_books = get_favorite_books(user_id, page, per_page)
        else:
            books_data, total_books = search_books(
                title=title_query,
                authors=author_query,
                isbn=isbn_query,
                genres=genres_query,
                page=page,
                per_page=per_page
            )

        return jsonify({
            'books': books_data,
            'total_books': total_books,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_books + per_page - 1) // per_page
        })

    except Exception as e:
        error_logger.error('Chyba při získávání knih: %s', str(e))
        return jsonify({'error': 'Nepodařilo se získat knihy'}), 500

@bp.route('/api/fetch_books', methods=['POST'])
def fetch_books():
    """
    Process and update book data received from a client.

    Expects a JSON payload containing book data.

    Returns:
    JSON object with a message indicating:
    - Number of books updated
    - Number of new books added

    Raises:
    400 Bad Request if no book data is provided
    500 Internal Server Error if there's an issue processing the books
    """
    info_logger.info('Zahájeno přijímání dat knih od klienta')
    try:
        books_data = request.get_json()
        if not books_data:
            error_logger.error('Chybějící data v požadavku')
            return jsonify({'error': 'Chybějící data v požadavku'}), 400

        updated_books, new_books = fetch_and_update_books(books_data)

        info_logger.info('Aktualizováno %d knih, přidáno %d nových knih', updated_books, new_books)
        return jsonify({
            'message': f'Aktualizováno {updated_books} knih, přidáno {new_books} nových knih'
        }), 200

    except Exception as e:
        error_logger.error('Výjimka při zpracování knih: %s', str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/api/books/<isbn>')
def get_book_endpoint(isbn):
    """
    Retrieve detailed information for a specific book by its ISBN.

    URL Parameters:
    - isbn (str): International Standard Book Number of the book

    Returns:
    JSON object containing:
    - book: Detailed book information
    
    Raises:
    404 Not Found if the book doesn't exist or is not visible to the user
    500 Internal Server Error if there's an issue retrieving the book details
    """
    try:
        book_data = get_book_by_isbn(isbn, session.get('user_id'))

        if not book_data:
            info_logger.warning('Kniha s ISBN %s nebyla nalezena nebo není viditelná', isbn)
            return jsonify({'error': 'Kniha nebyla nalezena'}), 404

        info_logger.info('Úspěšně získán detail knihy %s', isbn)
        return jsonify({'book': book_data})
    except Exception as e:
        error_logger.error('Chyba při získávání detailu knihy %s: %s', isbn, str(e))
        return jsonify({'error': 'Interní chyba serveru'}), 500

@bp.route('/api/genres')
def get_genres_endpoint():
    """
    Retrieve all unique book genres in the system.

    Returns:
    JSON object containing:
    - genres: List of all unique book genres
    - total_genres: Total number of unique genres
    
    Raises:
    500 Internal Server Error if there's an issue retrieving the genres
    """
    try:
        genres = get_all_unique_genres()

        info_logger.info('Úspěšně získány všechny unikátní žánry. Počet: %d', len(genres))

        return jsonify({
            'genres': genres,
            'total_genres': len(genres)
        })
    except Exception as e:
        error_logger.error('Chyba při získávání žánrů: %s', str(e))
        return jsonify({'error': 'Nepodařilo se získat žánry'}), 500
