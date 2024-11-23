import csv
import os
from sqlalchemy import or_
from database.book import db, Book
from database.user import favorite_books
from database.audit import AuditEventType
from database.audit_operations import create_audit_log
from sqlalchemy.exc import SQLAlchemyError

def get_favorite_books(user_id, page=1, per_page=25):
    try:
        base_query = db.session.query(Book).join(
            favorite_books,
            Book.ISBN10 == favorite_books.c.book_isbn10
        ).filter(
            favorite_books.c.user_id == user_id
        )
        
        total_books = base_query.count()
        books = base_query.order_by(Book.Title).offset((page - 1) * per_page).limit(per_page).all()
        
        books_data = _format_books_data(books)
        return books_data, total_books
    except SQLAlchemyError as e:
        print(f"Error getting favorite books: {str(e)}")
        return [], 0

def search_books(title=None, authors=None, isbn=None, genres=None, page=1, per_page=25):
    try:
        query = Book.query.filter_by(is_visible=True)

        if title:
            query = query.filter(Book.Title.ilike(f'%{title}%'))
        
        if authors:
            author_terms = [author.strip() for author in authors.split(';') if author.strip()]
            for author in author_terms:
                query = query.filter(Book.Author.ilike(f'%{author}%'))
        
        if isbn:
            query = query.filter(
                or_(
                    Book.ISBN10.ilike(f'%{isbn}%'),
                    Book.ISBN13.ilike(f'%{isbn}%')
                )
            )
        
        if genres:
            genre_terms = [genre.strip() for genre in genres.split(';') if genre.strip()]
            for genre in genre_terms:
                query = query.filter(Book.Genres.ilike(f'%{genre}%'))

        total = query.count()
        books = query.order_by(Book.Title).offset((page - 1) * per_page).limit(per_page).all()
        
        books_data = _format_books_data(books)
        return books_data, total
    except SQLAlchemyError as e:
        print(f"Error searching books: {str(e)}")
        return [], 0

def get_book_by_isbn(isbn, user_id=None):
    try:
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).filter_by(is_visible=True).first()
        
        if not book:
            return None
            
        is_favorite = False
        if user_id:
            favorite = db.session.query(favorite_books).filter_by(
                user_id=user_id,
                book_isbn10=book.ISBN10
            ).first()
            is_favorite = favorite is not None
            
        return _format_book_data(book, is_favorite)
    except SQLAlchemyError as e:
        print(f"Error getting book by ISBN: {str(e)}")
        return None

def fetch_and_update_books(books_data):
    try:
        previously_visible_books = {book.ISBN10: book.Title for book in Book.query.filter_by(is_visible=True).all()}
        new_visible_isbns = {book['isbn10'] for book in books_data if book.get('isbn10')}
        newly_added_books = set()
        
        updated_books = 0
        new_books = 0
        
        Book.query.update({Book.is_visible: False}, synchronize_session=False)
        
        for book in books_data:
            isbn10 = book.get('isbn10')
            if not isbn10:
                continue
                
            title = book.get('title')
            existing_book = Book.query.get(isbn10)
            
            if existing_book:
                _update_existing_book(existing_book, book)
                updated_books += 1
            else:
                new_book = _create_new_book(book)
                db.session.add(new_book)
                new_books += 1
                newly_added_books.add(isbn10)
                
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

        _create_audit_logs(previously_visible_books, new_visible_isbns, newly_added_books)
        
        db.session.commit()
        return updated_books, new_books
        
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def _format_books_data(books):
    return [{
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
        'Price': book.Price,
        'is_visible': book.is_visible
    } for book in books]

def _format_book_data(book, is_favorite=False):
    return {
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
        'Price': book.Price,
        'is_favorite': is_favorite
    }

def _update_existing_book(book, data):
    book.is_visible = data.get('price', 0) > 0
    book.ISBN13 = data.get('isbn13')
    book.Title = data.get('title')
    book.Author = data.get('authors') if isinstance(data.get('authors'), str) else '; '.join(data.get('authors', []))
    book.Genres = data.get('categories')
    book.Cover_Image = data.get('thumbnail')
    book.Description = data.get('description')
    book.Year_of_Publication = data.get('published_year')
    book.Number_of_Pages = data.get('num_pages')
    book.Average_Rating = data.get('average_rating')
    book.Number_of_Ratings = data.get('ratings_count')
    book.Price = data.get('price')

def _create_new_book(data):
    return Book(
        ISBN10=data.get('isbn10'),
        ISBN13=data.get('isbn13'),
        Title=data.get('title'),
        Author=data.get('authors') if isinstance(data.get('authors'), str) else '; '.join(data.get('authors', [])),
        Genres=data.get('categories'),
        Cover_Image=data.get('thumbnail'),
        Description=data.get('description'),
        Year_of_Publication=data.get('published_year'),
        Number_of_Pages=data.get('num_pages'),
        Average_Rating=data.get('average_rating'),
        Number_of_Ratings=data.get('ratings_count'),
        Price=data.get('price'),
        is_visible=data.get('price', 0) > 0
    )

def _create_audit_logs(previously_visible_books, new_visible_isbns, newly_added_books):
    for isbn, title in previously_visible_books.items():
        if isbn not in new_visible_isbns:
            create_audit_log(
                event_type=AuditEventType.BOOK_HIDE,
                username="CDB_SYSTEM",
                book_isbn=isbn,
                book_title=title
            )
            
    for isbn in new_visible_isbns:
        if isbn not in previously_visible_books and isbn not in newly_added_books:
            book = Book.query.get(isbn)
            if book:
                create_audit_log(
                    event_type=AuditEventType.BOOK_SHOW,
                    username="CDB_SYSTEM",
                    book_isbn=isbn,
                    book_title=book.Title
                )

# Ponecháváme původní funkci get_all_unique_genres, protože je již správně implementována
def get_all_unique_genres():
    try:
        books_with_genres = Book.query.filter(
            Book.Genres.isnot(None),
            Book.Genres != '',
            Book.is_visible == True
        ).with_entities(Book.Genres).all()
        
        unique_genres = set()
        
        for book in books_with_genres:
            if book.Genres:
                genres = [genre.strip() for genre in book.Genres.split(';') if genre.strip()]
                unique_genres.update(genres)
        
        return sorted(list(unique_genres))
    except SQLAlchemyError as e:
        print(f"Error getting unique genres: {str(e)}")
        return []