# app.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_migrate import Migrate

# Import modelů a databáze
from database import db
from database.book import Book
from database.user import User
from database.rating import Rating

# Import operací
from database.book_operations import get_all_books, search_books, add_book, get_all_unique_genres
from database.comment_operations import add_comment, get_comments_for_book, delete_comment
from database.user_operations import create_user, authenticate_user
from database.favorite_operations import toggle_favorite, get_user_favorite_books, is_book_favorite
from database.rating_operations import add_or_update_rating, get_user_rating

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

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True, origins=["http://localhost:3007"])

    # Konfigurace aplikace
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/mydatabase'
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    
    # Inicializace
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Nastavení logování
    setup_logging(app)
    
    return app

def setup_logging(app):
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Info logger
    info_handler = RotatingFileHandler(
        os.path.join(log_dir, 'info.log'), 
        maxBytes=5*1024*1024, 
        backupCount=5
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Error logger
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'), 
        maxBytes=5*1024*1024, 
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    app.logger.addHandler(info_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)

app = create_app()

# Základní endpointy
@app.route('/')
def hello_world():
    app.logger.info('Přístup na hlavní stránku')
    return 'Hello, World!'

# Knihy endpointy
@app.route('/api/books')
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    title_query = request.args.get('title', '')
    author_query = request.args.get('author', '')
    isbn_query = request.args.get('isbn', '')
    genres_query = request.args.get('genres', '')

    try:
        base_query = Book.query.filter_by(is_visible=True)

        if title_query:
            base_query = base_query.filter(Book.Title.ilike(f'%{title_query}%'))
        if author_query:
            base_query = base_query.filter(Book.Author.ilike(f'%{author_query}%'))
        if isbn_query:
            base_query = base_query.filter((Book.ISBN10.ilike(f'%{isbn_query}%')) | 
                                         (Book.ISBN13.ilike(f'%{isbn_query}%')))
        
        # Improved genre filtering
        if genres_query:
            genre_terms = [genre.strip() for genre in genres_query.split(';') if genre.strip()]
            if genre_terms:
                # Create a filter for each genre and combine them with AND
                for genre in genre_terms:
                    base_query = base_query.filter(Book.Genres.ilike(f'%{genre}%'))

        total_books = base_query.count()
        books = base_query.order_by(Book.Title).offset((page - 1) * per_page).limit(per_page).all()

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
            'Average_Rating': book.Average_Rating,
            'Number_of_Ratings': book.Number_of_Ratings,
        } for book in books]

        return jsonify({
            'books': books_data,
            'total_books': total_books,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_books + per_page - 1) // per_page
        })

    except Exception as e:
        error_logger.error('Chyba při získávání knih: %s', str(e))
        return jsonify({'error': 'Nepodařilo se získat knihy'}), 500
    
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
        - average_rating (float): Průměrné hodnocení knihy zákazníky.
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
                existing_book.Average_Rating = book.get('average_rating')
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
                    Average_Rating=book.get('average_rating'),
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

@app.route('/api/books/<isbn>')
def get_book_endpoint(isbn):
    try:
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).filter_by(is_visible=True).first()
        
        if not book:
            app.logger.warning('Kniha s ISBN %s nebyla nalezena nebo není viditelná', isbn)
            return jsonify({'error': 'Kniha nebyla nalezena'}), 404
            
        # Zjistíme, zda je kniha oblíbená pro přihlášeného uživatele
        is_favorite = False
        user_id = session.get('user_id')
        if user_id:
            is_favorite, _ = is_book_favorite(user_id, isbn)
            
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
            'Average_Rating': book.Average_Rating,
            'Number_of_Ratings': book.Number_of_Ratings,
            'is_favorite': is_favorite
        }
        
        app.logger.info('Úspěšně získán detail knihy %s', isbn)
        return jsonify({'book': book_data})
    except Exception as e:
        app.logger.error('Chyba při získávání detailu knihy %s: %s', isbn, str(e))
        return jsonify({'error': 'Interní chyba serveru'}), 500

@app.route('/api/genres')
def get_genres_endpoint():
    try:
        genres = get_all_unique_genres()
        
        app.logger.info('Úspěšně získány všechny unikátní žánry. Počet: %d', len(genres))
        
        return jsonify({
            'genres': genres,
            'total_genres': len(genres)
        })
    except Exception as e:
        app.logger.error('Chyba při získávání žánrů: %s', str(e))
        return jsonify({'error': 'Nepodařilo se získat žánry'}), 500
    
# Uživatelské endpointy
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
        app.logger.info('Nový uživatel %s byl registrován', username)
        return jsonify({'message': 'Uživatel úspěšně zaregistrován'}), 201
    app.logger.warning('Registrace uživatele %s selhala', username)
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
        app.logger.info('Uživatel %s se přihlásil', username)
        return jsonify({
            'message': 'Přihlášení úspěšné',
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name
            }
        }), 200
    app.logger.warning('Nepodařilo se přihlásit uživatele %s', username)
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
            return jsonify({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name
                }
            }), 200
    return jsonify({'error': 'Uživatel není přihlášen'}), 401

@app.route('/api/favorites', methods=['GET'])
def get_favorite_books_endpoint():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    
    books, total, error = get_user_favorite_books(user_id, page, per_page)
    
    if books is None:
        app.logger.error('Chyba při získávání oblíbených knih: %s', error)
        return jsonify({'error': error}), 400
        
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
        'Average_Rating': book.Average_Rating,
        'Number_of_Ratings': book.Number_of_Ratings,
    } for book in books]
    
    return jsonify({
        'books': books_data,
        'total_books': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/api/favorites/<isbn>', methods=['POST'])
def toggle_favorite_book_endpoint(isbn):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    success, message = toggle_favorite(user_id, isbn)
    
    if success:
        app.logger.info('Změněn stav oblíbené knihy %s pro uživatele %s', isbn, user_id)
        return jsonify({'message': message}), 200
    else:
        app.logger.warning(
            'Nepodařilo se změnit stav oblíbené knihy %s: %s',
            isbn, message
        )
        return jsonify({'error': message}), 400

@app.route('/api/favorites/<isbn>/status', methods=['GET'])
def check_favorite_status_endpoint(isbn):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    is_favorite, error = is_book_favorite(user_id, isbn)
    
    if error:
        app.logger.warning(
            'Nepodařilo se zjistit stav oblíbené knihy %s: %s',
            isbn, error
        )
        return jsonify({'error': error}), 400
        
    return jsonify({'is_favorite': is_favorite})


# Komentáře endpointy
@app.route('/api/comments/<isbn>', methods=['GET'])
def get_book_comments_endpoint(isbn):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    comments, total, message = get_comments_for_book(isbn, page, per_page)
    
    if comments is None:
        app.logger.warning('Kniha %s nebyla nalezena nebo není viditelná', isbn)
        return jsonify({'error': message}), 404
        
    comments_data = [{
        'id': comment.id,
        'text': comment.text,
        'created_at': comment.created_at.isoformat(),
        'user_id': comment.user_id
    } for comment in comments]
    
    return jsonify({
        'comments': comments_data,
        'total_comments': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/api/comments', methods=['POST'])
def add_book_comment_endpoint():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    data = request.json
    book_isbn = data.get('book_isbn')
    text = data.get('text')
    
    if not book_isbn or not text:
        return jsonify({'error': 'Chybí povinné údaje'}), 400
        
    success, message = add_comment(book_isbn, user_id, text)
    
    if success:
        app.logger.info('Uživatel %s přidal komentář ke knize %s', user_id, book_isbn)
        return jsonify({'message': message}), 201
    else:
        app.logger.warning(
            'Nepodařilo se přidat komentář ke knize %s: %s',
            book_isbn, message
        )
        return jsonify({'error': message}), 400

@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_book_comment_endpoint(comment_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    success, message = delete_comment(comment_id, user_id)
    
    if success:
        app.logger.info('Komentář %s byl smazán uživatelem %s', comment_id, user_id)
        return jsonify({'message': message}), 200
    else:
        app.logger.warning(
            'Nepodařilo se smazat komentář %s: %s',
            comment_id, message
        )
        return jsonify({'error': message}), 400
    
# Hodnocení Endpointy
@app.route('/api/ratings/<isbn>', methods=['POST'])
def rate_book_endpoint(isbn):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    data = request.json
    rating = data.get('rating')
    
    if not rating or not isinstance(rating, int) or not (1 <= rating <= 5):
        return jsonify({'error': 'Neplatné hodnocení'}), 400
        
    success, message = add_or_update_rating(user_id, isbn, rating)
    
    if success:
        app.logger.info('Uživatel %s ohodnotil knihu %s hodnocením %d', user_id, isbn, rating)
        return jsonify({'message': message}), 200
    else:
        app.logger.warning(
            'Nepodařilo se přidat hodnocení ke knize %s: %s',
            isbn, message
        )
        return jsonify({'error': message}), 400

@app.route('/api/ratings/<isbn>', methods=['GET'])
def get_user_rating_endpoint(isbn):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    rating, error = get_user_rating(user_id, isbn)
    
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify({'rating': rating})

# Inicializace databáze
with app.app_context():
    try:
        db.create_all()
        app.logger.info('Databázové tabulky byly úspěšně vytvořeny')
    except Exception as e:
        app.logger.error('Chyba při vytváření databázových tabulek: %s', str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8007, debug=True)