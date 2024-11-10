from sqlalchemy import func
from database import db
from database.book import Book
from database.rating import Rating

def add_or_update_rating(user_id, isbn, rating_value):
    """
    Add or update a user's rating for a book and recalculate book statistics.
    
    Args:
        user_id (int): The ID of the user rating the book
        isbn (str): The ISBN of the book being rated
        rating_value (int): Rating value (1-5)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # First find the book
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).first()
        
        if not book:
            return False, "Kniha nebyla nalezena"
            
        if not book.is_visible:
            return False, "Kniha není dostupná"
            
        # Check if user has already rated this book
        existing_rating = Rating.query.filter_by(
            user_id=user_id,
            book_isbn=book.ISBN13
        ).first()
        
        old_rating_sum = book.Average_Rating * book.Number_of_Ratings if book.Average_Rating and book.Number_of_Ratings else 0
        
        if existing_rating:
            # Update existing rating
            # Subtract old rating from sum before updating
            old_rating_sum = old_rating_sum - existing_rating.rating
            existing_rating.rating = rating_value
            # No change in total number of ratings
            new_count = book.Number_of_Ratings
        else:
            # Create new rating
            new_rating = Rating(
                user_id=user_id,
                book_isbn=book.ISBN13,
                rating=rating_value
            )
            db.session.add(new_rating)
            # Increment total number of ratings
            new_count = (book.Number_of_Ratings or 0) + 1
        
        # Commit to ensure rating is saved
        db.session.commit()
        
        # Add new rating to sum
        new_rating_sum = old_rating_sum + rating_value
        
        # Update book statistics with combined ratings
        book.Number_of_Ratings = new_count
        book.Average_Rating = new_rating_sum / new_count if new_count > 0 else None
        
        db.session.commit()
        
        return True, "Hodnocení bylo úspěšně uloženo"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Chyba při ukládání hodnocení: {str(e)}"

def get_user_rating(user_id, isbn):
    """
    Get a user's rating for a specific book.
    
    Args:
        user_id (int): The ID of the user
        isbn (str): The ISBN of the book
    
    Returns:
        tuple: (rating: int|None, error: str|None)
    """
    try:
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).first()
        
        if not book:
            return None, "Kniha nebyla nalezena"
            
        rating = Rating.query.filter_by(
            user_id=user_id,
            book_isbn=book.ISBN13
        ).first()
        
        return rating.rating if rating else None, None
        
    except Exception as e:
        return None, f"Chyba při získávání hodnocení: {str(e)}"