import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
from database.models import db, Book
from database.database_operations import get_all_books, search_books, load_mock_data_to_db, add_book
import requests

# Vytvoření a konfigurace aplikace
app = Flask(__name__)
CORS(app)

# Inicializace databáze
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/mydatabase'
db.init_app(app)

with app.app_context():
    db.create_all()
    # Load mock data into the database
    load_mock_data_to_db()

# Zajištění existence adresáře pro logy
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Konfigurace logování
info_handler = RotatingFileHandler(os.path.join(log_dir, 'info.log'), maxBytes=5*1024*1024, backupCount=5)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

error_handler = RotatingFileHandler(os.path.join(log_dir, 'error.log'), maxBytes=5*1024*1024, backupCount=5)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

info_logger = logging.getLogger('info_logger')
info_logger.setLevel(logging.INFO)
info_logger.addHandler(info_handler)

error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
error_logger.addHandler(error_handler)

@app.route('/')
def hello_world():
    info_logger.info('Přístup na hlavní stránku')
    return 'Hello, World!'

@app.route('/api/books')
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    search_query = request.args.get('search', '')
    
    info_logger.info(f'Požadavek na získání knih - Stránka: {page}, Počet na stránku: {per_page}, Vyhledávací dotaz: "{search_query}"')
    
    if search_query:
        books, total_books = search_books(search_query, page, per_page)
        info_logger.info(f'Vyhledávání knih - Nalezeno {total_books} výsledků pro dotaz: "{search_query}"')
    else:
        books, total_books = get_all_books(page, per_page)
        info_logger.info(f'Získání všech knih - Celkem {total_books} knih')
    
    if books is None:
        error_logger.error('Chyba při získávání knih z databáze')
        return jsonify({'error': 'Nepodařilo se získat knihy'}), 500

    books_data = [{
        'ISBN10': book.ISBN10,
        'ISBN13': book.ISBN13,
        'Title': book.Title,
        'Author': book.Author,
        'Genres': book.Genres,
        'Cover_Image': book.Cover_Image,
        'Description': book.Description,
        'Year_of_Publication': book.Year_of_Publication,
        'Number_of_Pages': book.Number_of_Pages,
        'Average_Customer_Rating': book.Average_Customer_Rating,
        'Number_of_Ratings': book.Number_of_Ratings,
    } for book in books]

    info_logger.info(f'Úspěšně vráceno {len(books_data)} knih')

    return jsonify({
        'books': books_data,
        'total_books': total_books,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_books + per_page - 1) // per_page
    })

@app.route('/api/fetch_books', methods=['GET'])
def fetch_books():
    info_logger.info('Zahájeno načítání knih z externí API')
    try:
        response = requests.get('http://wea.nti.tul.cz:1337/api/books')
        if response.status_code == 200:
            books_data = response.json()
            info_logger.info(f'Úspěšně načteno {len(books_data)} knih z externí API')

            saved_books = 0
            for book in books_data:
                isbn13 = book.get('isbn13')
                isbn10 = book.get('isbn10')
                title = book.get('title')
                authors = book.get('authors')
                categories = book.get('categories')
                thumbnail = book.get('thumbnail')
                description = book.get('description')
                published_year = book.get('published_year')
                num_pages = book.get('num_pages')
                average_rating = book.get('average_rating')
                ratings_count = book.get('ratings_count')

                # Převedení autorů na string, pokud je to list
                if isinstance(authors, list):
                    authors = '; '.join(authors)

                success, message = add_book(
                    isbn10=isbn10,
                    isbn13=isbn13,
                    title=title,
                    author=authors,
                    genres=categories,
                    cover_image=thumbnail,
                    description=description,
                    year_of_publication=published_year,
                    number_of_pages=num_pages,
                    average_customer_rating=average_rating,
                    number_of_ratings=ratings_count
                )

                if success:
                    saved_books += 1
                    info_logger.info(f'Kniha úspěšně uložena: {title} (ISBN13: {isbn13})')
                else:
                    error_logger.error(f'Chyba při ukládání knihy {isbn13}: {message}')

            info_logger.info(f'Celkem uloženo {saved_books} knih z {len(books_data)} načtených')
            return jsonify({'message': f'Úspěšně načteno a uloženo {saved_books} knih'}), 200
        else:
            error_logger.error(f'Chyba při načítání dat z externí API. Stavový kód: {response.status_code}')
            return jsonify({'error': 'Nepodařilo se načíst data z externí API'}), 500
    except requests.RequestException as e:
        error_logger.error(f'Výjimka při načítání knih z externí API: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8007, debug=True)