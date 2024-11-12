from flask import Blueprint, jsonify, request, session
from database.audit import AuditEventType
from database.audit_operations import create_audit_log
from database import db
from database.book import Book
from database.user import favorite_books
from database.book_operations import get_all_books, search_books, add_book, get_all_unique_genres
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
            base_query = db.session.query(Book).join(
                favorite_books,
                Book.ISBN10 == favorite_books.c.book_isbn10
            ).filter(
                favorite_books.c.user_id == user_id
            )
        else:
            base_query = Book.query.filter_by(is_visible=True)

        if title_query:
            base_query = base_query.filter(Book.Title.ilike(f'%{title_query}%'))
        if author_query:
            base_query = base_query.filter(Book.Author.ilike(f'%{author_query}%'))
        if isbn_query:
            base_query = base_query.filter((Book.ISBN10.ilike(f'%{isbn_query}%')) | 
                                         (Book.ISBN13.ilike(f'%{isbn_query}%')))
        
        if genres_query:
            genre_terms = [genre.strip() for genre in genres_query.split(';') if genre.strip()]
            if genre_terms:
                for genre in genre_terms:
                    base_query = base_query.filter(Book.Genres.ilike(f'%{genre}%'))

        total_books = base_query.count()
        books = base_query.order_by(Book.Title).offset((page - 1) * per_page).limit(per_page).all()

        books_data = [{
            'ISBN10': book.ISBN10,
            'ISBN13': book.ISBN13,
            'Title': book.Title,
            'Author': book.Author,
            'Genres': book.Genres,
            'Cover_Image': book.Cover_Image,
            'Description': book.Description,
            'Year_of_Publication': book.Year_of_Publication,
            'Number_of_Pages': book.Number_of_Pages,
            'Average_Rating': book.Average_Rating,
            'Number_of_Ratings': book.Number_of_Ratings,
            'is_visible': book.is_visible if show_favorites else True
        } for book in books]

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

        # Získáme seznam aktuálně viditelných knih
        previously_visible_books = {book.ISBN10: book.Title for book in Book.query.filter_by(is_visible=True).all()}
        # Seznam nových ISBN z příchozích dat
        new_visible_isbns = {book['isbn10'] for book in books_data if book.get('isbn10')}
        # Set pro sledování nově přidaných knih
        newly_added_books = set()
        
        updated_books = 0
        new_books = 0
        
        # Nastavíme všechny knihy jako neviditelné
        Book.query.update({Book.is_visible: False}, synchronize_session=False)
        
        # Zpracujeme nová data
        for book in books_data:
            isbn10 = book.get('isbn10')
            if not isbn10:
                continue
                
            title = book.get('title')
            existing_book = Book.query.get(isbn10)
            
            if existing_book:
                existing_book.is_visible = True
                existing_book.ISBN10 = isbn10
                existing_book.ISBN13 = book.get('isbn13')
                existing_book.Title = title
                existing_book.Author = book.get('authors') if isinstance(book.get('authors'), str) else '; '.join(book.get('authors', []))
                existing_book.Genres = book.get('categories')
                existing_book.Cover_Image = book.get('thumbnail')
                existing_book.Description = book.get('description')
                existing_book.Year_of_Publication = book.get('published_year')
                existing_book.Number_of_Pages = book.get('num_pages')
                existing_book.Average_Rating = book.get('average_rating')
                existing_book.Number_of_Ratings = book.get('ratings_count')
                updated_books += 1
            else:
                new_book = Book(
                    ISBN10=isbn10,
                    ISBN13=book.get('isbn13'),
                    Title=title,
                    Author=book.get('authors') if isinstance(book.get('authors'), str) else '; '.join(book.get('authors', [])),
                    Genres=book.get('categories'),
                    Cover_Image=book.get('thumbnail'),
                    Description=book.get('description'),
                    Year_of_Publication=book.get('published_year'),
                    Number_of_Pages=book.get('num_pages'),
                    Average_Rating=book.get('average_rating'),
                    Number_of_Ratings=book.get('ratings_count'),
                    is_visible=True
                )
                db.session.add(new_book)
                new_books += 1
                newly_added_books.add(isbn10)  # Přidáme do setu nových knih
                
                # Auditujeme přidání úplně nové knihy
                create_audit_log(
                    event_type=AuditEventType.BOOK_ADD,
                    username="CDB_SYSTEM",
                    book_isbn=isbn10,
                    book_title=title,
                    additional_data={
                        "author": new_book.Author,
                        "genres": new_book.Genres
                    }
                )

        # Porovnáme rozdíly a vytvoříme audit logy
        for isbn, title in previously_visible_books.items():
            if isbn not in new_visible_isbns:
                # Kniha byla skryta
                create_audit_log(
                    event_type=AuditEventType.BOOK_HIDE,
                    username="CDB_SYSTEM",
                    book_isbn=isbn,
                    book_title=title
                )
                
        for isbn in new_visible_isbns:
            if isbn not in previously_visible_books and isbn not in newly_added_books:
                # Kniha byla znovu zobrazena (ale není úplně nová)
                book = Book.query.get(isbn)
                if book:
                    create_audit_log(
                        event_type=AuditEventType.BOOK_SHOW,
                        username="CDB_SYSTEM",
                        book_isbn=isbn,
                        book_title=book.Title
                    )

        db.session.commit()
        info_logger.info('Aktualizováno %d knih, přidáno %d nových knih', updated_books, new_books)
        return jsonify({
            'message': f'Aktualizováno {updated_books} knih, přidáno {new_books} nových knih'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        error_logger.error('Výjimka při zpracování knih: %s', str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/api/books/<isbn>')
def get_book_endpoint(isbn):
    try:
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).filter_by(is_visible=True).first()
        
        if not book:
            info_logger.warning('Kniha s ISBN %s nebyla nalezena nebo není viditelná', isbn)
            return jsonify({'error': 'Kniha nebyla nalezena'}), 404
            
        # Zjistíme, zda je kniha oblíbená pro přihlášeného uživatele
        is_favorite = False
        user_id = session.get('user_id')
        if user_id:
            favorite = db.session.query(favorite_books).filter_by(
                user_id=user_id,
                book_isbn10=book.ISBN10
            ).first()
            is_favorite = favorite is not None
            
        book_data = {
            'ISBN10': book.ISBN10,
            'ISBN13': book.ISBN13,
            'Title': book.Title,
            'Author': book.Author,
            'Genres': book.Genres,
            'Cover_Image': book.Cover_Image,
            'Description': book.Description,
            'Year_of_Publication': book.Year_of_Publication,
            'Number_of_Pages': book.Number_of_Pages,
            'Average_Rating': book.Average_Rating,
            'Number_of_Ratings': book.Number_of_Ratings,
            'is_favorite': is_favorite
        }
        
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