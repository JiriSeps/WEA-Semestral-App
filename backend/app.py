import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
from database.models import db, Book
from database.database_operations import get_all_books, search_books
import requests


# Vytvoření a konfigurace aplikace
app = Flask(__name__)
CORS(app)

# Inicializace databáze
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/mydatabase'
db.init_app(app)

with app.app_context():
    db.create_all()

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
    info_logger.info('Zpráva pro logování: Hello, World!')
    error_logger.error('Testovací chybová zpráva')
    return 'Hello, World!'

@app.route('/api/books')
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    search_query = request.args.get('search', '')
    
    if search_query:
        books, total_books = search_books(search_query, page, per_page)
    else:
        books, total_books = get_all_books(page, per_page)
    
    if books is None:
        error_logger.error('Chyba při získávání knih z databáze')
        return jsonify({'error': 'Nepodařilo se získat knihy'}), 500

    books_data = [{
        'ISBN10': book['ISBN10'],
        'ISBN13': book['ISBN13'],
        'Title': book['Title'],
        'Author': book['Author'],
        'Genres': book['Genres'],
        'Cover_Image': book['Cover_Image'],
        'Description': book['Description'],
        'Year_of_Publication': book['Year_of_Publication'],
        'Number_of_Pages': book['Number_of_Pages'],
        'Average_Customer_Rating': book['Average_Customer_Rating'],
        'Number_of_Ratings': book['Number_of_Ratings'],
    } for book in books]

    return jsonify({
        'books': books_data,
        'total_books': total_books,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_books + per_page - 1) // per_page
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8007, debug=True)
