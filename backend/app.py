import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS
import os

# Vytvoření a konfigurace aplikace
app = Flask(__name__)
CORS(app)

# Zajištění existence adresáře pro logy
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Konfigurace logování
# Vytvoření handleru pro logy úrovně INFO
info_handler = RotatingFileHandler(os.path.join(log_dir, 'info.log'), maxBytes=5*1024*1024, backupCount=5)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Vytvoření handleru pro logy úrovně ERROR
error_handler = RotatingFileHandler(os.path.join(log_dir, 'error.log'), maxBytes=5*1024*1024, backupCount=5)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Vytvoření a konfigurace loggerů
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

if __name__ == '__main__':
    # V produkčním prostředí byste měli nastavit debug=False
    app.run(host='0.0.0.0', port=8007, debug=True)