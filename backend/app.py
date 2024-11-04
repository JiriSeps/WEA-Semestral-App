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
from database.comment_operations import add_comment, delete_comment, get_comments_for_book
from database import db
from database.book import Book
from database.user import User

# Vytvoření a konfigurace aplikace
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3007"])

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
    books = Book.query.filter_by(is_visible=True).paginate(page=page, per_page=per_page, error_out=False)
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
    query = Book.query.filter_by(is_visible=True)
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

# Upravená funkce fetch_books pro správu viditelnosti knih
@app.route('/api/fetch_books', methods=['POST'])
def fetch_books():
    """
    Přidá nové knihy do databáze z příchozího JSON požadavku.
    Nejprve nastaví všem knihám viditelnost na false, poté aktivuje pouze knihy z příchozího souboru.

    JSON Body (pole knih):
        - isbn10 (str): ISBN10 číslo knihy.
        - isbn13 (str): ISBN13 číslo knihy.
        - title (str): Název knihy.
        - author (str): Autor knihy.
        - genres (str): Žánry knihy (oddělené středníkem).
        - cover_image (str): URL obrázku obálky knihy.
        - description (str): Popis knihy.
        - year_of_publication (int): Rok vydání knihy.
        - number_of_pages (int): Počet stránek knihy.
        - average_customer_rating (float): Průměrné hodnocení knihy zákazníky.
        - number_of_ratings (int): Počet hodnocení zákazníky.

    Returns:
        dict: JSON objekt s informací o úspěšnosti operace nebo chybová zpráva.
    """
    info_logger.info('Zahájeno přijímání dat knih od klienta')
    try:
        books_data = request.get_json()
        if not books_data:
            error_logger.error('Chybějící data v požadavku')
            return jsonify({'error': 'Chybějící data v požadavku'}), 400

        # Nejprve nastavíme všem knihám viditelnost na false
        Book.query.update({Book.is_visible: False}, synchronize_session=False)
        
        updated_books = 0
        new_books = 0
        
        for book in books_data:
            isbn10 = book.get('isbn10')
            if not isbn10:
                continue
                
            existing_book = Book.query.get(isbn10)
            
            if existing_book:
                # Aktualizujeme existující knihu a nastavíme ji jako viditelnou
                existing_book.is_visible = True
                existing_book.ISBN10 = isbn10
                existing_book.ISBN13 = book.get('isbn13')
                existing_book.Title = book.get('title')
                existing_book.Author = book.get('authors') if isinstance(book.get('authors'), str) else '; '.join(book.get('authors', []))
                existing_book.Genres = book.get('categories')
                existing_book.Cover_Image = book.get('thumbnail')
                existing_book.Description = book.get('description')
                existing_book.Year_of_Publication = book.get('published_year')
                existing_book.Number_of_Pages = book.get('num_pages')
                existing_book.Average_Customer_Rating = book.get('average_rating')
                existing_book.Number_of_Ratings = book.get('ratings_count')
                updated_books += 1
            else:
                # Přidáme novou knihu
                new_book = Book(
                    ISBN10=isbn10,
                    ISBN13=book.get('isbn13'),
                    Title=book.get('title'),
                    Author=book.get('authors') if isinstance(book.get('authors'), str) else '; '.join(book.get('authors', [])),
                    Genres=book.get('categories'),
                    Cover_Image=book.get('thumbnail'),
                    Description=book.get('description'),
                    Year_of_Publication=book.get('published_year'),
                    Number_of_Pages=book.get('num_pages'),
                    Average_Customer_Rating=book.get('average_rating'),
                    Number_of_Ratings=book.get('ratings_count'),
                    is_visible=True
                )
                db.session.add(new_book)
                new_books += 1

        db.session.commit()
        info_logger.info('Aktualizováno %d knih, přidáno %d nových knih', updated_books, new_books)
        return jsonify({
            'message': f'Aktualizováno {updated_books} knih, přidáno {new_books} nových knih'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        error_logger.error('Výjimka při zpracování knih: %s', str(e))
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

@app.route('/api/books/<isbn>')
def get_book(isbn):
    """
    Získá detail knihy podle ISBN.
    
    Args:
        isbn (str): ISBN10 nebo ISBN13 knihy.
        
    Returns:
        dict: JSON objekt obsahující detaily knihy nebo chybovou zprávu.
    """
    try:
        book = Book.query.filter((Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)).first()
        
        if not book:
            info_logger.warning('Kniha s ISBN %s nebyla nalezena', isbn)
            return jsonify({'error': 'Kniha nebyla nalezena'}), 404
            
        book_data = {
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
        }
        
        info_logger.info('Úspěšně získán detail knihy %s', isbn)
        return jsonify({'book': book_data})
    except Exception as e:
        error_logger.error('Chyba při získávání detailu knihy %s: %s', isbn, str(e))
        return jsonify({'error': 'Interní chyba serveru'}), 500
    
    # Nové endpointy pro komentáře
@app.route('/api/comments/<isbn>', methods=['GET'])
def get_book_comments(isbn):
    """
    Získá komentáře ke knize.
    
    Args:
        isbn (str): ISBN10 knihy
        
    Query Parameters:
        page (int): Číslo stránky (výchozí: 1)
        per_page (int): Počet komentářů na stránku (výchozí: 10)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    try:
        comments, total, message = get_comments_for_book(isbn, page, per_page)
        
        if comments is None:
            info_logger.warning('Kniha %s nebyla nalezena nebo není viditelná', isbn)
            return jsonify({'error': message}), 404
            
        comments_data = [{
            'id': comment.id,
            'text': comment.text,
            'created_at': comment.created_at.isoformat(),
            'user_id': comment.user_id
        } for comment in comments]
        
        info_logger.info('Úspěšně získány komentáře pro knihu %s', isbn)
        return jsonify({
            'comments': comments_data,
            'total_comments': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        error_logger.error('Chyba při získávání komentářů ke knize %s: %s', isbn, str(e))
        return jsonify({'error': 'Interní chyba serveru'}), 500

@app.route('/api/comments', methods=['POST'])
def add_book_comment():
    """
    Přidá nový komentář ke knize.
    Vyžaduje přihlášeného uživatele.
    
    JSON Body:
        book_isbn (str): ISBN10 knihy
        text (str): Text komentáře
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    data = request.json
    book_isbn = data.get('book_isbn')
    text = data.get('text')
    
    if not book_isbn or not text:
        return jsonify({'error': 'Chybí povinné údaje'}), 400
        
    try:
        success, message = add_comment(book_isbn, user_id, text)
        
        if success:
            info_logger.info('Uživatel %s přidal komentář ke knize %s', user_id, book_isbn)
            return jsonify({'message': message}), 201
        else:
            info_logger.warning('Nepodařilo se přidat komentář ke knize %s: %s', book_isbn, message)
            return jsonify({'error': message}), 400
    except Exception as e:
        error_logger.error('Chyba při přidávání komentáře: %s', str(e))
        return jsonify({'error': 'Interní chyba serveru'}), 500

@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_book_comment(comment_id):
    """
    Smaže komentář.
    Vyžaduje přihlášeného uživatele a vlastnictví komentáře.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    try:
        success, message = delete_comment(comment_id, user_id)
        
        if success:
            info_logger.info('Komentář %s byl smazán uživatelem %s', comment_id, user_id)
            return jsonify({'message': message}), 200
        else:
            info_logger.warning('Nepodařilo se smazat komentář %s: %s', comment_id, message)
            return jsonify({'error': message}), 400
    except Exception as e:
        error_logger.error('Chyba při mazání komentáře %s: %s', comment_id, str(e))
        return jsonify({'error': 'Interní chyba serveru'}), 500
    

# Vytvoření tabulek při spuštění aplikace
with app.app_context():
    try:
        db.create_all()
        info_logger.info('Databázové tabulky byly úspěšně vytvořeny')
    except Exception as e:
        error_logger.error('Chyba při vytváření databázových tabulek: %s', str(e))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8007, debug=True)
