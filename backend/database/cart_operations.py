from . import db
from .book import Book
from .user import User, books_in_cart
from datetime import datetime
from sqlalchemy import select, exists

def get_formatted_shopping_cart(user_id, page=1, per_page=25):
    """
    Získá formátovaný seznam knih v košíku včetně metadat pro stránkování.
    Vrací pouze viditelné knihy.
    """
    books, total, error = get_user_shopping_cart(user_id, page, per_page)
    
    if books is None:
        return {'error': error}
    
    # Filtrujeme pouze viditelné knihy
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
    
    return {
        'books': books_data,
        'total_books': len(filtered_books),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(filtered_books) + per_page - 1) // per_page
    }

def toggle_cart(user_id, isbn):
    """
    Přepne stav knihy v košíku - pokud je v košíku, odebere ji, pokud není, přidá ji
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Uživatel nenalezen'}
            
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).first()
        if not book:
            return {'error': 'Kniha nenalezena'}
            
        if not book.is_visible:
            return {'error': 'Kniha není dostupná'}
        
        exists_stmt = select(books_in_cart).where(
            db.and_(
                books_in_cart.c.user_id == user_id,
                books_in_cart.c.book_isbn10 == book.ISBN10
            )
        ).exists()
        is_in_cart = db.session.query(exists_stmt).scalar()
        
        if is_in_cart:
            stmt = books_in_cart.delete().where(
                db.and_(
                    books_in_cart.c.user_id == user_id,
                    books_in_cart.c.book_isbn10 == book.ISBN10
                )
            )
            db.session.execute(stmt)
            action = 'odebrána z'
        else:
            stmt = books_in_cart.insert().values(
                user_id=user_id,
                book_isbn10=book.ISBN10,
                added_at=datetime.utcnow()
            )
            db.session.execute(stmt)
            action = 'přidána do'
            
        db.session.commit()
        
        return {
            'message': f'Kniha byla {action} košíku',
            'is_in_cart': not is_in_cart,
            'book': {
                'ISBN10': book.ISBN10,
                'Title': book.Title,
                'Price': book.Price
            }
        }
    except Exception as e:
        db.session.rollback()
        return {'error': f'Chyba při změně stavu knihy v košíku: {str(e)}'}

def get_user_shopping_cart(user_id, page=1, per_page=25):
    """
    Získá seznam knih v košíku uživatele
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return None, 0, "Uživatel nenalezen"
        
        query = db.session.query(Book, Book.is_visible).join(
            books_in_cart,
            Book.ISBN10 == books_in_cart.c.book_isbn10
        ).filter(
            books_in_cart.c.user_id == user_id
        )
        
        total = query.count()
        
        results = query.order_by(books_in_cart.c.added_at.desc()).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        books = [{
            'book': book,
            'is_visible': is_visible
        } for book, is_visible in results]
        
        return books, total, None
    except Exception as e:
        return None, 0, f"Chyba při získávání knih v košíku: {str(e)}"

def is_book_in_shopping_cart(user_id, isbn):
    """
    Zkontroluje, zda je kniha v košíku u daného uživatele
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Uživatel nenalezen'}
            
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).first()
        if not book:
            return {'error': 'Kniha nenalezena'}
            
        if not book.is_visible:
            return {'error': 'Kniha není dostupná'}
        
        exists_stmt = select(books_in_cart).where(
            db.and_(
                books_in_cart.c.user_id == user_id,
                books_in_cart.c.book_isbn10 == book.ISBN10
            )
        ).exists()
        is_in_cart = db.session.query(exists_stmt).scalar()
            
        return {
            'is_in_cart': is_in_cart,
            'book': {
                'ISBN10': book.ISBN10,
                'Title': book.Title,
                'Price': book.Price
            } if is_in_cart else None
        }
    except Exception as e:
        return {'error': f'Chyba při kontrole knihy v košíku: {str(e)}'}