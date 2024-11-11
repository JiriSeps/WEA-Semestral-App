from database.user import db, User, Gender
from database.book import Book
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def create_user(username, password, name):
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, name=name)
    db.session.add(new_user)
    try:
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {str(e)}")
        return None

def find_user_by_username(username):
    return User.query.filter_by(username=username).first()

def authenticate_user(username, password):
    user = find_user_by_username(username)
    if user and check_password_hash(user.password, password):
        return user
    return None

def update_user_profile(user_id, data):
    """
    Aktualizuje kompletní profil uživatele na základě poskytnutých dat.
    
    Args:
        user_id: ID uživatele k aktualizaci
        data: Dictionary obsahující aktualizované údaje:
            - personal_street, personal_city, personal_postal_code, personal_country
            - billing_street, billing_city, billing_postal_code, billing_country
            - gdpr_consent (bool)
            - gender ('male' nebo 'female')
            - age (int)
            - favorite_genres (list)
            - referral_source
    
    Returns:
        User: Aktualizovaný uživatel nebo None v případě chyby
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return None

        # Osobní adresa
        user.personal_street = data.get('personal_street')
        user.personal_city = data.get('personal_city')
        user.personal_postal_code = data.get('personal_postal_code')
        user.personal_country = data.get('personal_country')
        
        # Fakturační adresa
        user.billing_street = data.get('billing_street')
        user.billing_city = data.get('billing_city')
        user.billing_postal_code = data.get('billing_postal_code')
        user.billing_country = data.get('billing_country')
        
        # GDPR souhlas
        if 'gdpr_consent' in data:
            user.gdpr_consent = bool(data['gdpr_consent'])
            if user.gdpr_consent:
                user.gdpr_consent_date = datetime.utcnow()
        
        # Gender - převod stringu na enum
        if 'gender' in data:
            gender_str = data['gender'].lower()
            if gender_str in ('male', 'female'):
                user.gender = Gender[gender_str.upper()]
        
        # Věk
        if 'age' in data:
            try:
                user.age = int(data['age'])
            except (ValueError, TypeError):
                pass  # Ignorujeme neplatný věk
        
        # Oblíbené žánry
        if 'favorite_genres' in data:
            user.favorite_genres = data['favorite_genres']
        
        # Zdroj reference
        if 'referral_source' in data:
            user.referral_source = data['referral_source']
        
        db.session.commit()
        return user
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating user profile: {str(e)}")
        return None