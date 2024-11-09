#!/bin/bash
set -e

echo "Waiting for database..."
wait-for-it db:5432 -t 60

echo "Running database migrations..."
# Inicializace pouze pokud neexistuje
if [ ! -d "migrations" ] || [ -z "$(ls -A migrations)" ]; then
    echo "Initializing migrations directory..."
    flask db init
fi

echo "Creating new migration..."
flask db migrate || true

echo "Applying migrations..."
flask db upgrade

echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8007 app:app