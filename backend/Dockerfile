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

# Kopírování celého projektu
COPY . .

# Nastavení proměnných prostředí
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py

# Vytvoření adresáře pro migrations
RUN mkdir -p migrations

# Spuštění aplikace a migrací v jednom příkazu
CMD ["bash", "-c", "\
    echo 'Waiting for database...' && \
    wait-for-it db:5432 -t 60 && \
    echo 'Running database migrations...' && \
    PGPASSWORD=password psql -h db -U user -d mydatabase -c 'DROP TABLE IF EXISTS alembic_version;' && \
    if [ ! -d 'migrations' ] || [ -z \"$(ls -A migrations)\" ]; then \
        echo 'Initializing migrations directory...' && \
        flask db init; \
    fi && \
    echo 'Creating new migration...' && \
    flask db migrate || true && \
    echo 'Applying migrations...' && \
    flask db upgrade && \
    echo 'Starting Gunicorn server...' && \
    exec gunicorn --bind 0.0.0.0:8007 app:app \
"]