import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
from database.models import db, Book
from database.database_operations import get_all_books

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
    books = get_all_books()  # Uses mock data in development mode
    if books is None:
        error_logger.error('Chyba při získávání knih z databáze')
        return jsonify({'error': 'Nepodařilo se získat knihy'}), 500

    # Create the books_data list correctly using dictionary keys
    books_data = [{
        'ISBN10': book['ISBN10'],
        'ISBN13': book['ISBN13'],
        'Title': book['Title'],
        'Author': book['Author'],
        'Genres': book['Genres'],
        'Cover_Image': book['Cover_Image'],
        'Description': book['Description'],
        'Critics_Rating': book['Critics_Rating'],
        'Year_of_Publication': book['Year_of_Publication'],
        'Number_of_Pages': book['Number_of_Pages'],
        'Average_Customer_Rating': book['Average_Customer_Rating'],
    } for book in books]

    return jsonify(books_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8007, debug=True)
