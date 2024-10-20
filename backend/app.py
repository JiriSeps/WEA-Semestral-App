import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, session
from flask_cors import CORS
import os
from werkzeug.security import generate_password_hash, check_password_hash
import requests

# Import modelů
from database import db
from database.book import Book
from database.user import User

# Vytvoření a konfigurace aplikace
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Inicializace databáze
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/mydatabase'
app.config['SECRET_KEY'] = 'your_secret_key_here'  # V produkci použijte bezpečný tajný klíč
db.init_app(app)

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

# Funkce pro práci s databází
def get_all_books(page, per_page):
    books = Book.query.paginate(page=page, per_page=per_page, error_out=False)
    return books.items, books.total

def search_books(title, authors, isbn, page, per_page):
    query = Book.query
    if title:
        query = query.filter(Book.Title.ilike(f'%{title}%'))
    if authors:
        query = query.filter(Book.Author.ilike(f'%{authors}%'))
    if isbn:
        query = query.filter((Book.ISBN10 == isbn) | (Book.ISBN13 == isbn))
    books = query.paginate(page=page, per_page=per_page, error_out=False)
    return books.items, books.total

def add_book(isbn10, isbn13, title, author, genres, cover_image, description, year_of_publication, number_of_pages, average_customer_rating, number_of_ratings):
    try:
        new_book = Book(
            ISBN10=isbn10,
            ISBN13=isbn13,
            Title=title,
            Author=author,
            Genres=genres,
            Cover_Image=cover_image,
            Description=description,
            Year_of_Publication=year_of_publication,
            Number_of_Pages=number_of_pages,
            Average_Customer_Rating=average_customer_rating,
            Number_of_Ratings=number_of_ratings
        )
        db.session.add(new_book)
        db.session.commit()
        return True, "Kniha úspěšně přidána"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def create_user(username, password, name):
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, name=name)
    db.session.add(new_user)
    try:
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        error_logger.error(f"Error creating user: {str(e)}")
        return None

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

# Endpointy
@app.route('/')
def hello_world():
    info_logger.info('Přístup na hlavní stránku')
    return 'Hello, World!'

@app.route('/api/books')
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    title_query = request.args.get('title', '')
    author_query = request.args.get('author', '')
    isbn_query = request.args.get('isbn', '')
    
    info_logger.info(f'Požadavek na získání knih - Stránka: {page}, Počet na stránku: {per_page}')
    info_logger.info(f'Vyhledávací parametry - Název: "{title_query}", Autor: "{author_query}", ISBN: "{isbn_query}"')
    
    if title_query or author_query or isbn_query:
        books, total_books = search_books(
            title=title_query,
            authors=author_query,
            isbn=isbn_query,
            page=page,
            per_page=per_page
        )
        info_logger.info(f'Vyhledávání knih - Nalezeno {total_books} výsledků')
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

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    
    if not username or not password or not name:
        return jsonify({'error': 'Všechna pole jsou povinná'}), 400
    
    user = create_user(username, password, name)
    if user:
        info_logger.info(f'Nový uživatel zaregistrován: {username}')
        return jsonify({'message': 'Uživatel úspěšně zaregistrován'}), 201
    else:
        error_logger.error(f'Chyba při registraci uživatele: {username}')
        return jsonify({'error': 'Registrace se nezdařila'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Uživatelské jméno a heslo jsou povinné'}), 400
    
    user = authenticate_user(username, password)
    if user:
        session['user_id'] = user.id
        info_logger.info(f'Uživatel přihlášen: {username}')
        return jsonify({'message': 'Přihlášení úspěšné', 'user': {'id': user.id, 'username': user.username, 'name': user.name}}), 200
    else:
        error_logger.error(f'Neúspěšný pokus o přihlášení: {username}')
        return jsonify({'error': 'Neplatné přihlašovací údaje'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Odhlášení úspěšné'}), 200

@app.route('/api/user', methods=['GET'])
def get_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({'user': {'id': user.id, 'username': user.username, 'name': user.name}}), 200
    return jsonify({'error': 'Uživatel není přihlášen'}), 401

# Vytvoření tabulek při spuštění aplikace
with app.app_context():
    try:
        db.create_all()
        info_logger.info('Databázové tabulky byly úspěšně vytvořeny')
    except Exception as e:
        error_logger.error(f'Chyba při vytváření databázových tabulek: {str(e)}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8007, debug=True)