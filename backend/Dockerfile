# Použijeme officiální Python image
FROM python:3.9-slim

# Nastavení pracovního adresáře
WORKDIR /app

# Instalace systémových závislostí včetně PostgreSQL klienta
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalace wait-for-it
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

# Kopírování requirements a instalace závislostí
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

# Kopírování init skriptu a nastavení práv
COPY init-db.sh .
RUN chmod +x init-db.sh

# Kopírování celého projektu
COPY . .

# Nastavení proměnných prostředí
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py

# Vytvoření adresáře pro migrations, pokud neexistuje
RUN mkdir -p migrations

# Inicializace Flask-Migrate (pokud ještě není inicializován)
RUN flask db init || true

# Spuštění init skriptu při startu kontejneru
CMD ["./init-db.sh"]