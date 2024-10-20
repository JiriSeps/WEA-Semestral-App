# Použijeme oficiální Python image
FROM python:3.9-slim

# Nastav pracovní adresář
WORKDIR /app

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Počkat na databázi a pak spustit aplikaci
CMD ["sh", "-c", "wait-for-it db:5432 && python app.py"]