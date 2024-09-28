# Použijeme oficiální Python image
FROM python:3.9-slim

# Nastav pracovní adresář
WORKDIR /app

# Zkopíruj requirements.txt a nainstaluj závislosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Zkopíruj ostatní soubory
COPY . .

# Spusť Flask aplikaci
CMD ["python", "app.py"]
