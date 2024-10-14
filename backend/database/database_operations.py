import csv
import os
from database.models import db, Book
from sqlalchemy.exc import SQLAlchemyError

# Funkce pro načtení mockovaných dat z CSV souboru
def load_mock_data():
    mock_data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'data_mock.csv')
    
    books = []
    
    with open(mock_data_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row if your CSV has headers
        for row in reader:
            # Ensure correct indexing based on the CSV structure
            isbn13 = row[0]  # ISBN13
            isbn10 = row[1]  # ISBN10
            title = row[2]  # Title
            author = row[4]  # Author
            genres = row[5]  # Genres
            cover_image = row[6]  # Cover_Image
            description = row[7]  # Description
            year_of_publication = int(row[8]) if row[8] else None  # Year_of_Publication
            critics_rating = float(row[9]) if row[9] else None  # Critics_Rating
            number_of_pages = int(row[10]) if row[10] else None  # Number_of_Pages
            average_customer_rating = int(row[11]) if row[11] else None  # Average_Customer_Rating

            book = {
                'ISBN10': isbn10,
                'ISBN13': isbn13,
                'Title': title,
                'Author': author,
                'Genres': genres,
                'Cover_Image': cover_image,
                'Description': description,
                'Critics_Rating': critics_rating,
                'Year_of_Publication': year_of_publication,
                'Number_of_Pages': number_of_pages,
                'Average_Customer_Rating': average_customer_rating,
            }
            
            books.append(book)
    
    return books


# Funkce pro přidání knihy do databáze
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

# Funkce pro získání knihy podle ISBN10
def get_book_by_isbn10(isbn10):
    try:
        book = Book.query.get(isbn10)
        return book
    except SQLAlchemyError as e:
        return None

# Funkce pro aktualizaci knihy
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

# Funkce pro odstranění knihy
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

# Funkce pro získání všech knih (z reálné databáze nebo mock dat)
def get_all_books():
    if os.getenv('FLASK_ENV') == 'development':
        # Pokud je prostředí ve vývojovém režimu, načti mock data
        return load_mock_data()
    else:
        try:
            books = Book.query.all()
            return books
        except SQLAlchemyError as e:
            return None

# Funkce pro vyhledávání knih
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
