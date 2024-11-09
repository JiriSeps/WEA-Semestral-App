from . import db
from .book import Book
from .user import User

def toggle_favorite(user_id, isbn):
    """
    Přepne stav oblíbené knihy - pokud je oblíbená, odebere ji, pokud není, přidá ji
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "Uživatel nenalezen"
            
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).first()
        if not book:
            return False, "Kniha nenalezena"
            
        is_favorite = book in user.favorite_books
        
        if is_favorite:
            user.favorite_books.remove(book)
            message = "Kniha byla odebrána z oblíbených"
        else:
            user.favorite_books.append(book)
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
        user = User.query.get(user_id)
        if not user:
            return None, 0, "Uživatel nenalezen"
            
        # Získáme počet všech oblíbených knih
        total = user.favorite_books.count()
        
        # Získáme konkrétní stránku
        favorite_books = user.favorite_books.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return favorite_books.items, total, None
    except Exception as e:
        return None, 0, f"Chyba při získávání oblíbených knih: {str(e)}"

def is_book_favorite(user_id, isbn):
    """
    Zkontroluje, zda je kniha v oblíbených u daného uživatele
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "Uživatel nenalezen"
            
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).first()
        if not book:
            return False, "Kniha nenalezena"
            
        return book in user.favorite_books, None
    except Exception as e:
        return False, f"Chyba při kontrole oblíbené knihy: {str(e)}"