import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_session import Session
from database import db

# Import blueprintů
from routes import books, users, comments, ratings, favorites, shopping_cart, orders

def setup_logging(app):
   """
    Configure logging for the Flask application.

    This function sets up two rotating file loggers:
    1. An INFO level logger for general application logs
    2. An ERROR level logger for recording error events

    Args:
        app (Flask): The Flask application instance to configure logging for

    Key Features:
    - Creates a 'logs' directory if it doesn't exist
    - Uses RotatingFileHandler to manage log file sizes
    - Logs are rotated when they reach 5MB
    - Up to 5 backup log files are maintained
    - Logs include timestamp, log level, and message
    """
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
   """
    Create and configure the Flask application.

    This function is responsible for:
    - Initializing the Flask application
    - Configuring CORS
    - Setting up database connection
    - Configuring session management
    - Setting up logging
    - Registering application blueprints

    Returns:
        Flask: Fully configured Flask application instance

    Configuration Details:
    - CORS enabled for specific origins
    - Database URI from environment or default
    - Secure random secret key generation
    - Filesystem-based session management
    - Database initialization
    - Blueprint registration for different app modules
    """
   app = Flask(__name__)

   # CORS configuration - povolíme oba origins podle prostředí
   CORS(app, supports_credentials=True, origins=[
       "http://localhost:3007",
       "http://wea.nti.tul.cz:3007"
   ])

   # Application configuration
   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@sk08-db/mydatabase')
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
   app.register_blueprint(orders.bp)

   return app

# Create app instance
app = create_app()

@app.route('/')
def hello_world():
   """
    Default route for the application.

    Logs an info message when the root endpoint is accessed
    and returns a simple greeting.

    Returns:
        str: A greeting message
    """
   app.logger.info('Přístup na hlavní stránku')
   return 'Hello, World!'

# Database initialization
with app.app_context():
   """
    Initialize database tables within the application context.

    Attempts to create all database tables defined in the models.
    Logs a success message or captures and logs any errors during
    table creation.
    """
   try:
       db.create_all()
       app.logger.info('Databázové tabulky byly úspěšně vytvořeny')
   except Exception as e:
       app.logger.error('Chyba při vytváření databázových tabulek: %s', str(e))

if __name__ == '__main__':
   """
    Entry point for running the Flask application.

    Starts the development server with:
    - Host set to '0.0.0.0' (accessible from outside localhost)
    - Port 8007
    - Debug mode enabled
    """
   app.run(host='0.0.0.0', port=8007, debug=True)
