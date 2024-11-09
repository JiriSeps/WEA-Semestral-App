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

# Import operací
from database.book_operations import get_all_books, search_books, add_book, get_all_unique_genres
from database.comment_operations import add_comment, get_comments_for_book, delete_comment
from database.user_operations import create_user, authenticate_user
from database.favorite_operations import toggle_favorite, get_user_favorite_books, is_book_favorite

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
def get_books_endpoint():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    title_query = request.args.get('title', '')
    author_query = request.args.get('author', '')
    isbn_query = request.args.get('isbn', '')
    genres_query = request.args.get('genres', '')

    app.logger.info(
        'Požadavek na získání knih - Stránka: %d, Počet na stránku: %d', 
        page, per_page
    )

    if title_query or author_query or isbn_query or genres_query:
        books, total_books = search_books(
            title=title_query,
            authors=author_query,
            isbn=isbn_query,
            genres=genres_query,
            page=page,
            per_page=per_page
        )
    else:
        books, total_books = get_all_books(page, per_page)

    if books is None:
        app.logger.error('Chyba při získávání knih z databáze')
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

@app.route('/api/books/<isbn>')
def get_book_endpoint(isbn):
    try:
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).first()
        
        if not book:
            app.logger.warning('Kniha s ISBN %s nebyla nalezena', isbn)
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
            'Average_Customer_Rating': book.Average_Customer_Rating,
            'Number_of_Ratings': book.Number_of_Ratings,
            'is_favorite': is_favorite  # Přidáno
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
        'Average_Customer_Rating': book.Average_Customer_Rating,
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

# Inicializace databáze
with app.app_context():
    try:
        db.create_all()
        app.logger.info('Databázové tabulky byly úspěšně vytvořeny')
    except Exception as e:
        app.logger.error('Chyba při vytváření databázových tabulek: %s', str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8007, debug=True)