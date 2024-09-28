import logging
from flask import Flask
from flask_cors import CORS

# Vytvoření a konfigurace aplikace
app = Flask(__name__)
CORS(app)

# Konfigurace logování
logging.basicConfig(
    filename='app.log',  # Zde zvolíš cestu pro logovací soubor
    level=logging.INFO,   # Úroveň logování (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formát logovacích zpráv
)

@app.route('/')
def hello_world():
    app.logger.info('Zpráva pro logování: Hello, World!')  # Logování zprávy
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
