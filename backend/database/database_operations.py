from database.models import db, Book
from sqlalchemy.exc import SQLAlchemyError

def add_book(isbn10, isbn13, title, author, genres=None, cover_image=None, critics_rating=None, 
             year_of_publication=None, number_of_pages=None, average_customer_rating=None, number_of_ratings=None):
    try:
        new_book = Book(
            ISBN10=isbn10,
            ISBN13=isbn13,
            Title=title,
            Author=author,
            Genres=genres,
            Cover_Image=cover_image,
            Critics_Rating=critics_rating,
            Year_of_Publication=year_of_publication,
            Number_of_Pages=number_of_pages,
            Average_Customer_Rating=average_customer_rating,
            Number_of_Ratings=number_of_ratings
        )
        db.session.add(new_book)
        db.session.commit()
        return True, "Book added successfully"
    except SQLAlchemyError as e:
        db.session.rollback()
        return False, str(e)

def get_book_by_isbn10(isbn10):
    try:
        book = Book.query.get(isbn10)
        return book
    except SQLAlchemyError as e:
        return None

def update_book(isbn10, **kwargs):
    try:
        book = Book.query.get(isbn10)
        if book:
            for key, value in kwargs.items():
                setattr(book, key, value)
            db.session.commit()
            return True, "Book updated successfully"
        else:
            return False, "Book not found"
    except SQLAlchemyError as e:
        db.session.rollback()
        return False, str(e)

def delete_book(isbn10):
    try:
        book = Book.query.get(isbn10)
        if book:
            db.session.delete(book)
            db.session.commit()
            return True, "Book deleted successfully"
        else:
            return False, "Book not found"
    except SQLAlchemyError as e:
        db.session.rollback()
        return False, str(e)

def get_all_books():
    try:
        books = Book.query.all()
        return books
    except SQLAlchemyError as e:
        return None

def search_books(query):
    try:
        books = Book.query.filter(
            (Book.Title.ilike(f'%{query}%')) |
            (Book.Author.ilike(f'%{query}%')) |
            (Book.ISBN10.ilike(f'%{query}%')) |
            (Book.ISBN13.ilike(f'%{query}%'))
        ).all()
        return books
    except SQLAlchemyError as e:
        return None