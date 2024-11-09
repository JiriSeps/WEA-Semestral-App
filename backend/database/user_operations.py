from database.user import db, User
from database.book import Book
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(username, password, name):
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, name=name)
    db.session.add(new_user)
    try:
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {str(e)}")
        return None

def find_user_by_username(username):
    return User.query.filter_by(username=username).first()

def authenticate_user(username, password):
    user = find_user_by_username(username)
    if user and check_password_hash(user.password, password):
        return user
    return None

# Operace s oblíbenými knihami
def add_favorite_book(user_id, isbn10):
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
            
        book = Book.query.get(isbn10)
        if not book:
            return False, "Book not found"
            
        if book not in user.favorite_books:
            user.favorite_books.append(book)
            db.session.commit()
            return True, "Book added to favorites"
        return False, "Book already in favorites"
    except Exception as e:
        db.session.rollback()
        return False, f"Error adding favorite: {str(e)}"

def remove_favorite_book(user_id, isbn10):
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
            
        book = Book.query.get(isbn10)
        if not book:
            return False, "Book not found"
            
        if book in user.favorite_books:
            user.favorite_books.remove(book)
            db.session.commit()
            return True, "Book removed from favorites"
        return False, "Book not in favorites"
    except Exception as e:
        db.session.rollback()
        return False, f"Error removing favorite: {str(e)}"

def get_user_favorites(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
            
        return user.favorite_books.all(), None
    except Exception as e:
        return None, f"Error getting favorites: {str(e)}"

def is_book_favorite(user_id, isbn10):
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
            
        book = Book.query.get(isbn10)
        if not book:
            return False, "Book not found"
            
        return book in user.favorite_books, None
    except Exception as e:
        return False, f"Error checking favorite status: {str(e)}"