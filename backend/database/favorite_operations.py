from . import db
from .book import Book
from .user import User, favorite_books
from datetime import datetime
from sqlalchemy import select, exists

def toggle_favorite(user_id, isbn):
    """
    Přepne stav oblíbené knihy - pokud je oblíbená, odebere ji, pokud není, přidá ji
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
        
        # Kontrola existence v oblíbených - opravená syntaxe pro novější SQLAlchemy
        exists_stmt = select(favorite_books).where(
            db.and_(
                favorite_books.c.user_id == user_id,
                favorite_books.c.book_isbn10 == book.ISBN10
            )
        ).exists()
        is_favorite = db.session.query(exists_stmt).scalar()
        
        if is_favorite:
            # Odstranění z oblíbených
            stmt = favorite_books.delete().where(
                db.and_(
                    favorite_books.c.user_id == user_id,
                    favorite_books.c.book_isbn10 == book.ISBN10
                )
            )
            db.session.execute(stmt)
            message = "Kniha byla odebrána z oblíbených"
        else:
            # Přidání do oblíbených
            stmt = favorite_books.insert().values(
                user_id=user_id,
                book_isbn10=book.ISBN10,
                added_at=datetime.utcnow()
            )
            db.session.execute(stmt)
            
            message = "Kniha byla přidána do oblíbených"
            
        db.session.commit()
        return True, message
    except Exception as e:
        db.session.rollback()
        return False, f"Chyba při změně stavu oblíbené knihy: {str(e)}"

def get_user_favorite_books(user_id, page=1, per_page=25):
    """
    Získá seznam oblíbených knih uživatele s stránkováním
    """
    try:
        # Kontrola existence uživatele
        user = User.query.get(user_id)
        if not user:
            return None, 0, "Uživatel nenalezen"
        
        # Dotaz na oblíbené knihy s připojením tabulky knih
        query = db.session.query(Book).join(
            favorite_books,
            Book.ISBN10 == favorite_books.c.book_isbn10
        ).filter(
            favorite_books.c.user_id == user_id
        )
        
        # Celkový počet oblíbených knih
        total = query.count()
        
        # Stránkování
        books = query.order_by(favorite_books.c.added_at.desc()).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return books, total, None
    except Exception as e:
        return None, 0, f"Chyba při získávání oblíbených knih: {str(e)}"

def is_book_favorite(user_id, isbn):
    """
    Zkontroluje, zda je kniha v oblíbených u daného uživatele
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
        
        # Kontrola existence v oblíbených - opravená syntaxe pro novější SQLAlchemy
        exists_stmt = select(favorite_books).where(
            db.and_(
                favorite_books.c.user_id == user_id,
                favorite_books.c.book_isbn10 == book.ISBN10
            )
        ).exists()
        is_favorite = db.session.query(exists_stmt).scalar()
            
        return is_favorite, None
    except Exception as e:
        return False, f"Chyba při kontrole oblíbené knihy: {str(e)}"