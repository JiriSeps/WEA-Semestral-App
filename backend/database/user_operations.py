from database.user import db, User, Gender 
from database.book import Book
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database.genre import Genre

# user_operations.py

def format_user_data(user):
    """Helper funkce pro formátování dat uživatele"""
    return {
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'personal_address': {
            'street': user.personal_street,
            'city': user.personal_city,
            'postal_code': user.personal_postal_code,
            'country': user.personal_country
        },
        'billing_address': {
            'street': user.billing_street,
            'city': user.billing_city,
            'postal_code': user.billing_postal_code,
            'country': user.billing_country
        },
        'gdpr_consent': user.gdpr_consent,
        'gender': user.gender.value if user.gender else None,
        'age': user.age,
        'favorite_genres': [genre.name for genre in user.favorite_genres],  # Seznam názvů oblíbených žánrů
        'referral_source': user.referral_source
    }

def create_user(username, password, name):
    try:
        if User.query.filter_by(username=username).first():
            return {'error': 'Uživatelské jméno již existuje'}

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, name=name)
        db.session.add(new_user)
        db.session.commit()
        
        return {
            'message': 'Uživatel úspěšně zaregistrován',
            'user': format_user_data(new_user)
        }
    except Exception as e:
        db.session.rollback()
        return {'error': f'Chyba při vytváření uživatele: {str(e)}'}

def authenticate_user(username, password):
    try:
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return {
                'message': 'Přihlášení úspěšné',
                'user': format_user_data(user)
            }
        return {'error': 'Neplatné přihlašovací údaje'}
    except Exception as e:
        return {'error': f'Chyba při autentizaci: {str(e)}'}

def get_user_profile(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Uživatel nenalezen'}
        return format_user_data(user)
    except Exception as e:
        return {'error': f'Chyba při získávání profilu: {str(e)}'}

def get_formatted_user_data(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Uživatel nenalezen'}
        
        return {'user': format_user_data(user)}
    except Exception as e:
        return {'error': f'Chyba při získávání dat uživatele: {str(e)}'}

def update_user_profile(user_id, data):
    """
    Aktualizuje profil uživatele na základě poskytnutých dat.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Uživatel nenalezen'}

        # Osobní adresa - přímý přístup k atributům
        user.personal_street = data.get('personal_street')
        user.personal_city = data.get('personal_city')
        user.personal_postal_code = data.get('personal_postal_code')
        user.personal_country = data.get('personal_country')
        
        # Fakturační adresa - přímý přístup k atributům
        user.billing_street = data.get('billing_street')
        user.billing_city = data.get('billing_city')
        user.billing_postal_code = data.get('billing_postal_code')
        user.billing_country = data.get('billing_country')
        
        # GDPR souhlas
        if 'gdpr_consent' in data:
            user.gdpr_consent = bool(data['gdpr_consent'])
            if user.gdpr_consent:
                user.gdpr_consent_date = datetime.utcnow()
        
        # Gender
        if 'gender' in data:
            gender_str = data['gender'].lower()
            if gender_str in ('male', 'female'):
                user.gender = Gender[gender_str.upper()]
        
        # Věk
        if 'age' in data:
            try:
                user.age = int(data['age'])
            except (ValueError, TypeError):
                pass
        
        # Oblíbené žánry
        if 'favorite_genres' in data:
            genre_names = data['favorite_genres']
            if isinstance(genre_names, list):
                # Najdeme všechny existující žánry podle jejich názvů
                genres = Genre.query.filter(Genre.name.in_(genre_names)).all()
                
                # Vytvoříme slovník pro rychlé vyhledávání existujících žánrů
                existing_genres = {genre.name: genre for genre in genres}
                
                # Vytvoříme nové žánry pro ty, které ještě neexistují
                new_genres = []
                for name in genre_names:
                    if name not in existing_genres:
                        new_genre = Genre(name=name, is_active=True)
                        db.session.add(new_genre)
                        new_genres.append(new_genre)
                
                # Aktualizujeme oblíbené žánry uživatele
                user.favorite_genres = list(existing_genres.values()) + new_genres
        
        # Zdroj reference
        if 'referral_source' in data:
            user.referral_source = data['referral_source']
        
        db.session.commit()
        
        return {
            'message': 'Profil byl úspěšně aktualizován',
            'user': format_user_data(user)
        }
        
    except Exception as e:
        db.session.rollback()
        return {'error': f'Chyba při aktualizaci profilu: {str(e)}'}