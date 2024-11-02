from database.comment import db, Comment
from database.book import Book
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

def add_comment(book_isbn, user_id, text):
    """
    Přidá nový komentář ke knize.
    Kontroluje, zda je kniha viditelná před přidáním komentáře.
    """
    try:
        # Nejprve zkontrolujeme, zda kniha existuje a je viditelná
        book = Book.query.get(book_isbn)
        if not book:
            return False, "Book not found"
        if not book.is_visible:
            return False, "Book is not available for comments"

        new_comment = Comment(
            book_isbn=book_isbn,
            user_id=user_id,
            text=text,
            created_at=datetime.utcnow()
        )
        db.session.add(new_comment)
        db.session.commit()
        return True, "Comment added successfully"
    except SQLAlchemyError as e:
        db.session.rollback()
        return False, str(e)

def get_comments_for_book(book_isbn, page=1, per_page=10):
    """
    Získá všechny komentáře pro danou knihu s stránkováním.
    Vrací pouze komentáře pro viditelné knihy.
    """
    try:
        book = Book.query.get(book_isbn)
        if not book:
            return None, 0, "Book not found"
        if not book.is_visible:
            return None, 0, "Book is not visible"

        paginated_comments = Comment.query.filter_by(book_isbn=book_isbn)\
            .order_by(Comment.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return paginated_comments.items, paginated_comments.total, "Success"
    except SQLAlchemyError as e:
        return None, 0, str(e)

def delete_comment(comment_id, user_id):
    """
    Smaže komentář.
    Kontroluje, zda komentář patří danému uživateli.
    """
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return False, "Comment not found"
        if comment.user_id != user_id:
            return False, "Unauthorized to delete this comment"
            
        db.session.delete(comment)
        db.session.commit()
        return True, "Comment deleted successfully"
    except SQLAlchemyError as e:
        db.session.rollback()
        return False, str(e)

def get_user_comments(user_id, page=1, per_page=10):
    """
    Získá všechny komentáře od konkrétního uživatele.
    Vrací pouze komentáře k viditelným knihám.
    """
    try:
        query = Comment.query.join(Book)\
            .filter(Comment.user_id == user_id)\
            .filter(Book.is_visible == True)\
            .order_by(Comment.created_at.desc())
            
        paginated_comments = query.paginate(page=page, per_page=per_page, error_out=False)
        return paginated_comments.items, paginated_comments.total, "Success"
    except SQLAlchemyError as e:
        return None, 0, str(e)

def get_recent_comments(limit=5):
    """
    Získá nejnovější komentáře napříč všemi viditelnými knihami.
    """
    try:
        recent_comments = Comment.query.join(Book)\
            .filter(Book.is_visible == True)\
            .order_by(Comment.created_at.desc())\
            .limit(limit)\
            .all()
        return recent_comments, "Success"
    except SQLAlchemyError as e:
        return None, str(e)

def count_comments_for_book(book_isbn):
    """
    Spočítá celkový počet komentářů pro danou knihu.
    """
    try:
        count = Comment.query.filter_by(book_isbn=book_isbn).count()
        return count
    except SQLAlchemyError as e:
        print(f"Error counting comments: {str(e)}")
        return 0