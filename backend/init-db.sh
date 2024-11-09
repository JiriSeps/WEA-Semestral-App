#!/bin/bash
# init-db.sh

# Počkáme na dostupnost databáze
wait-for-it db:5432

# Provedeme migrace
flask db init || true
flask db migrate
flask db upgrade

# Spustíme aplikaci
gunicorn --bind 0.0.0.0:8007 app:app