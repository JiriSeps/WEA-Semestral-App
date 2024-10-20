"""
Aplikace pro správu knih a interakci s externím API pro získání informací o knihách.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, session
from flask_cors import CORS
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
    """
    Získá všechny knihy z databáze s paginací.

    Args:
        page (int): Číslo stránky.
        per_page (int): Počet knih na stránku.

    Returns:
        tuple: Seznam knih a celkový počet knih.
    """
    books = Book.query.paginate(page=page, per_page=per_page, error_out=False)
    return books.items, books.total

def search_books(title, authors, isbn, page, per_page):
    """
    Hledá knihy na základě zadaných parametrů.

    Args:
        title (str): Název knihy.
        authors (str): Autor knihy.
        isbn (str): ISBN knihy.
        page (int): Číslo stránky.
        per_page (int): Počet knih na stránku.

    Returns:
        tuple: Seznam knih a celkový počet knih.
    """
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
    """
    Přidá novou knihu do databáze.

    Args:
        isbn10 (str): ISBN10 knihy.
        isbn13 (str): ISBN13 knihy.
        title (str): Název knihy.
        author (str): Autor knihy.
        genres (str): Žánry knihy.
        cover_image (str): URL obálky knihy.
        description (str): Popis knihy.
        year_of_publication (int): Rok publikace.
        number_of_pages (int): Počet stránek.
        average_customer_rating (float): Průměrné hodnocení zákazníků.
        number_of_ratings (int): Počet hodnocení.

    Returns:
        tuple: Stav a zpráva o výsledku operace.
    """
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
    """
    Vytvoří nového uživatele.

    Args:
        username (str): Uživatelské jméno.
        password (str): Heslo.
        name (str): Jméno uživatele.

    Returns:
        User: Vytvořený uživatel nebo None při chybě.
    """
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, name=name)
    db.session.add(new_user)
    try:
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        error_logger.error('Chyba při vytváření uživatele: %s', str(e))
        return None

def authenticate_user(username, password):
    """
    Ověří uživatelské jméno a heslo.

    Args:
        username (str): Uživatelské jméno.
        password (str): Heslo.

    Returns:
        User: Ověřený uživatel nebo None.
    """
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

# Endpointy
@app.route('/')
def hello_world():
    """
    Vrací základní uvítací zprávu.

    Returns:
        str: Textová zpráva "Hello, World!".
    """
    info_logger.info('Přístup na hlavní stránku')
    return 'Hello, World!'

@app.route('/api/books')
def get_books():
    """
    Získá seznam knih, buď všechny knihy nebo vyhledá specifické podle parametrů.
    
    Query Parameters:
        title (str): Název knihy (volitelné).
        author (str): Autor knihy (volitelné).
        isbn (str): ISBN knihy (volitelné).
        page (int): Číslo stránky (výchozí: 1).
        per_page (int): Počet knih na stránku (výchozí: 25).

    Returns:
        dict: JSON objekt obsahující seznam knih a další metadata stránkování.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    title_query = request.args.get('title', '')
    author_query = request.args.get('author', '')
    isbn_query = request.args.get('isbn', '')

    info_logger.info('Požadavek na získání knih - Stránka: %d, Počet na stránku: %d', page, per_page)
    info_logger.info('Vyhledávací parametry - Název: "%s", Autor: "%s", ISBN: "%s"', title_query, author_query, isbn_query)

    if title_query or author_query or isbn_query:
        books, total_books = search_books(
            title=title_query,
            authors=author_query,
            isbn=isbn_query,
            page=page,
            per_page=per_page
        )
        info_logger.info('Vyhledávání knih - Nalezeno %d výsledků', total_books)
    else:
        books, total_books = get_all_books(page, per_page)
        info_logger.info('Získání všech knih - Celkem %d knih', total_books)

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
    """
    Přidá novou knihu do databáze.
    
    JSON Body:
        isbn10 (str): ISBN10 číslo knihy.
        isbn13 (str): ISBN13 číslo knihy.
        title (str): Název knihy.
        author (str): Autor knihy.
        genres (str): Žánry knihy (oddělené středníkem).
        cover_image (str): URL obrázku obálky knihy.
        description (str): Popis knihy.
        year_of_publication (int): Rok vydání knihy.
        number_of_pages (int): Počet stránek knihy.
        average_customer_rating (float): Průměrné hodnocení knihy zákazníky.
        number_of_ratings (int): Počet hodnocení zákazníky.

    Returns:
        dict: JSON objekt s informací o úspěšnosti operace nebo chybová zpráva.
    """
    info_logger.info('Zahájeno načítání knih z externí API')
    try:
        response = requests.get('http://wea.nti.tul.cz:1337/api/books', timeout=10)
        if response.status_code == 200:
            books_data = response.json()
            info_logger.info('Úspěšně načteno %d knih z externí API', len(books_data))

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
                    info_logger.info('Kniha úspěšně uložena: %s (ISBN13: %s)', title, isbn13)
                else:
                    error_logger.error('Chyba při ukládání knihy %s: %s', isbn13, message)

            info_logger.info('Celkem uloženo %d knih z %d načtených', saved_books, len(books_data))
            return jsonify({'message': f'Úspěšně načteno a uloženo {saved_books} knih'}), 200
        error_logger.error('Chyba při načítání dat z externí API. Stavový kód: %d', response.status_code)
        return jsonify({'error': 'Nepodařilo se načíst data z externí API'}), 500
    except requests.RequestException as e:
        error_logger.error('Výjimka při načítání knih z externí API: %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """
    Zaregistruje nového uživatele.

    JSON Body:
        username (str): Uživatelské jméno.
        password (str): Heslo.
        name (str): Jméno uživatele.

    Returns:
        dict: JSON objekt s informací o úspěšnosti registrace nebo chybová zpráva.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')

    if not username or not password or not name:
        return jsonify({'error': 'Všechna pole jsou povinná'}), 400

    user = create_user(username, password, name)
    if user:
        info_logger.info('Nový uživatel %s byl registrován', username)
        return jsonify({'message': 'Uživatel úspěšně zaregistrován'}), 201
    error_logger.warning('Registrace uživatele %s selhala', username)
    return jsonify({'error': 'Registrace se nezdařila'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    """
    Přihlásí uživatele.

    JSON Body:
        username (str): Uživatelské jméno.
        password (str): Heslo.

    Returns:
        dict: JSON objekt s informací o úspěšnosti přihlášení nebo chybová zpráva.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Uživatelské jméno a heslo jsou povinné'}), 400

    user = authenticate_user(username, password)
    if user:
        session['user_id'] = user.id
        info_logger.info('Uživatel %s se přihlásil', username)
        return jsonify({'message': 'Přihlášení úspěšné', 'user': {'id': user.id, 'username': user.username, 'name': user.name}}), 200
    error_logger.warning('Nepodařilo se přihlásit uživatele %s', username)
    return jsonify({'error': 'Neplatné přihlašovací údaje'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """
    Odhlásí uživatele.

    Returns:
        dict: JSON objekt s potvrzením o odhlášení.
    """
    session.pop('user_id', None)
    return jsonify({'message': 'Odhlášení úspěšné'}), 200

@app.route('/api/user', methods=['GET'])
def get_user():
    """
    Získání informací o aktuálně přihlášeném uživateli.

    Returns:
        Response: JSON odpověď obsahující informace o uživateli, pokud je přihlášen,
        nebo chybovou zprávu, pokud není přihlášen.
    """
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
        error_logger.error('Chyba při vytváření databázových tabulek: %s', str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8007, debug=True)
