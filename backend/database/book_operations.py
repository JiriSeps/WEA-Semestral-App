import csv
import os

from sqlalchemy import or_
from database.book import db, Book
from sqlalchemy.exc import SQLAlchemyError

# Funkce pro načtení mockovaných dat z CSV souboru
def load_mock_data_to_db():
    mock_data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'data_mock.csv')
    
    with open(mock_data_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            isbn13 = row[0]
            isbn10 = row[1]
            title = row[2]
            author = row[4]
            genres = row[5]
            cover_image = row[6]
            description = row[7]
            year_of_publication = int(row[8]) if row[8] else None
            average_customer_rating = float(row[9]) if row[9] else None
            number_of_pages = int(row[10]) if row[10] else None
            number_of_ratings = int(row[11]) if row[11] else None

            
            book = Book(
                ISBN10=isbn10,
                ISBN13=isbn13,
                Title=title,
                Author=author,
                Genres=genres,
                Cover_Image=cover_image,
                Description=description,
                Year_of_Publication=year_of_publication,
                Number_of_Pages=number_of_pages,
                Average_Rating=average_customer_rating,
                Number_of_Ratings=number_of_ratings
            )
            
            db.session.add(book)
    
    try:
        db.session.commit()
        print("Mock data loaded successfully")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error loading mock data: {str(e)}")


# Funkce pro přidání knihy do databáze
def add_book(isbn10, isbn13, title, author, genres=None, cover_image=None, critics_rating=None, 
             year_of_publication=None, number_of_pages=None, average_rating=None, number_of_ratings=None):
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
            Average_Rating=average_rating,
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
def get_all_books(page=1, per_page=25):
    try:
        books = Book.query.paginate(page=page, per_page=per_page, error_out=False)
        return books.items, books.total
    except SQLAlchemyError as e:
        print(f"Error getting all books: {str(e)}")
        return None, 0

def search_books(title=None, authors=None, isbn=None, genres=None, page=1, per_page=25):
    try:
        query = Book.query

        if title:
            query = query.filter(Book.Title.ilike(f'%{title}%'))
        
        if authors:
            author_terms = [author.strip() for author in authors.split(';')]
            author_filters = [Book.Author.ilike(f'%{author}%') for author in author_terms]
            if author_filters:
                query = query.filter(or_(*author_filters))
        
        if isbn:
            query = query.filter(
                or_(
                    Book.ISBN10.ilike(f'%{isbn}%'),
                    Book.ISBN13.ilike(f'%{isbn}%')
                )
            )
        
        if genres:
            genre_terms = [genre.strip() for genre in genres.split(';')]
            genre_filters = [Book.Genres.ilike(f'%{genre}%') for genre in genre_terms]
            if genre_filters:
                query = query.filter(or_(*genre_filters))

        # Execute query with pagination
        paginated_books = query.paginate(page=page, per_page=per_page, error_out=False)
        return paginated_books.items, paginated_books.total
    except SQLAlchemyError as e:
        print(f"Error searching books: {str(e)}")
        return None, 0

    
def get_all_unique_genres():
    try:
        # Získej všechny neprázdné žánry z databáze
        books_with_genres = Book.query.filter(
            Book.Genres.isnot(None),
            Book.Genres != ''
        ).with_entities(Book.Genres).all()
        
        # Set pro uložení unikátních žánrů
        unique_genres = set()
        
        # Projdi všechny knihy a jejich žánry
        for book in books_with_genres:
            # Předpokládáme, že žánry jsou odděleny čárkou
            if book.Genres:
                # Rozdělení žánrů a odstranění mezer
                genres = [genre.strip() for genre in book.Genres.split(';')]
                # Přidání do setu (automaticky odstraní duplikáty)
                unique_genres.update(genres)
        
        # Převeď set na seřazený seznam
        return sorted(list(unique_genres))
    except SQLAlchemyError as e:
        print(f"Error getting unique genres: {str(e)}")
        return []