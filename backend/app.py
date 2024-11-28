import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_session import Session
from database import db

# Import blueprintů
from routes import books, users, comments, ratings, favorites, shopping_cart

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

def create_app():
    app = Flask(__name__)
    
    # CORS configuration
    CORS(app, supports_credentials=True, origins=["http://localhost:3007"])

    # Application configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/mydatabase'
    app.config['SECRET_KEY'] = os.urandom(24)  # More secure random secret key
    
    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), 'sessions')
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    Session(app)  # Initialize Flask-Session
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    app.register_blueprint(books.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(comments.bp)
    app.register_blueprint(ratings.bp)
    app.register_blueprint(favorites.bp)
    app.register_blueprint(shopping_cart.bp)
    
    return app

# Create app instance
app = create_app()

@app.route('/')
def hello_world():
    app.logger.info('Přístup na hlavní stránku')
    return 'Hello, World!'

# Database initialization
with app.app_context():
    try:
        db.create_all()
        app.logger.info('Databázové tabulky byly úspěšně vytvořeny')
    except Exception as e:
        app.logger.error('Chyba při vytváření databázových tabulek: %s', str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8007, debug=True)