from flask import Blueprint, jsonify, request, session
from database.audit import AuditEventType
from database.audit_operations import create_audit_log
from database.book_operations import (
    search_books,
    get_book_by_isbn,
    get_all_unique_genres,
    fetch_and_update_books,
    get_favorite_books
)
import logging

bp = Blueprint('books', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/books')
def get_books():
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