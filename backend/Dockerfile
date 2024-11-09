# Použijeme officiální Python image
FROM python:3.9-slim

# Nastavení pracovního adresáře
WORKDIR /app

# Instalace systémových závislostí
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalace wait-for-it
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

# Kopírování requirements a instalace závislostí
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

# Kopírování celého projektu
COPY . .

# Vytvoření a nastavení init skriptu
COPY init-db.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/init-db.sh

# Nastavení proměnných prostředí
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py

# Vytvoření adresáře pro migrations, pokud neexistuje
RUN mkdir -p migrations

# Inicializace Flask-Migrate (pokud ještě není inicializován)
RUN flask db init || true

# Spuštění init skriptu při startu kontejneru
CMD ["init-db.sh"]