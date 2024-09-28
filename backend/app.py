from flask import Flask

app = Flask(__name__)

@app.route('/')  # Definice endpointu
def hello_world():
    return 'Hello, World!'  # Odpověď pro tento endpoint

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
