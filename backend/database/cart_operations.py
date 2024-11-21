from . import db
from .book import Book
from .user import User, books_in_cart
from datetime import datetime
from sqlalchemy import select, exists

def toggle_cart(user_id, isbn):
    """
    Přepne stav knihy do košíku - pokud je v košíku, odebere ji, pokud není, přidá ji
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "Uživatel nenalezen"
            
        # Hledáme knihu podle ISBN10 nebo ISBN13
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).first()
        if not book:
            return False, "Kniha nenalezena"
        
        # Kontrola existence v košíku - opravená syntaxe pro novější SQLAlchemy
        exists_stmt = select(books_in_cart).where(
            db.and_(
                books_in_cart.c.user_id == user_id,
                books_in_cart.c.book_isbn10 == book.ISBN10
            )
        ).exists()
        is_favorite = db.session.query(exists_stmt).scalar()
        
        if is_favorite:
            # Odstranění z košíku
            stmt = books_in_cart.delete().where(
                db.and_(
                    books_in_cart.c.user_id == user_id,
                    books_in_cart.c.book_isbn10 == book.ISBN10
                )
            )
            db.session.execute(stmt)
            message = "Kniha byla odebrána z košíku"
        else:
            # Přidání do košíku
            stmt = books_in_cart.insert().values(
                user_id=user_id,
                book_isbn10=book.ISBN10,
                added_at=datetime.utcnow()
            )
            db.session.execute(stmt)
            
            message = "Kniha byla přidána do košíku"
            
        db.session.commit()
        return True, message
    except Exception as e:
        db.session.rollback()
        return False, f"Chyba při změně stavu knihy v košíku: {str(e)}"

def get_user_shopping_cart(user_id, page=1, per_page=25):
    try:
        user = User.query.get(user_id)
        if not user:
            return None, 0, "Uživatel nenalezen"
        
        # Přidáme is_visible do výběru
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
        
        # Upravíme výstup, aby obsahoval informaci o viditelnosti
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
        # Kontrola existence uživatele
        user = User.query.get(user_id)
        if not user:
            return False, "Uživatel nenalezen"
            
        # Hledáme knihu podle ISBN10 nebo ISBN13
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).first()
        if not book:
            return False, "Kniha nenalezena"
        
        # Kontrola existence v košíku
        exists_stmt = select(books_in_cart).where(
            db.and_(
                books_in_cart.c.user_id == user_id,
                books_in_cart.c.book_isbn10 == book.ISBN10
            )
        ).exists()
        is_in_cart = db.session.query(exists_stmt).scalar()
            
        return is_in_cart, None
    except Exception as e:
        return False, f"Chyba při kontrole knihy v košíku: {str(e)}"