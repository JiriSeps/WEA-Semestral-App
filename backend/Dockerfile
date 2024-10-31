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

# Kopírování requirements
COPY requirements.txt .

# Instalace Python závislostí
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

# Kopírování celého projektu
COPY . .

# Nastavení proměnných prostředí
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Spuštění aplikace přes Gunicorn
CMD ["sh", "-c", "wait-for-it db:5432 && gunicorn --bind 0.0.0.0:8007 app:app"]