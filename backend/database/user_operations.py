from database.user import db, User, Gender
from database.book import Book
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database.genre import Genre

# user_operations.py

def format_user_data(user):
    """
    Helper function for formatting user data
    """
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
        'favorite_genres': [genre.name for genre in user.favorite_genres],  # List of favorite genres
        'referral_source': user.referral_source,
        'role': user.role.value if user.role else None  # Role of the user
    }

def create_user(username, password, name, role='USER'):
    try:
        if User.query.filter_by(username=username).first():
            return {'error': 'Username already exists'}

        hashed_password = generate_password_hash(password)
        if role not in ('USER', 'ADMIN'):
            return {'error': 'Invalid role'}

        new_user = User(username=username, password=hashed_password, name=name, role=role)
        db.session.add(new_user)
        db.session.commit()

        return {
            'message': 'User successfully registered',
            'user': format_user_data(new_user)
        }
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error creating user: {str(e)}'}

def authenticate_user(username, password):
    try:
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return {
                'message': 'Login successful',
                'user': format_user_data(user)
            }
        return {'error': 'Invalid login credentials'}
    except Exception as e:
        return {'error': f'Error during authentication: {str(e)}'}

def get_user_profile(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}
        return format_user_data(user)
    except Exception as e:
        return {'error': f'Error retrieving profile: {str(e)}'}
    
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
    Updates the user's profile based on the provided data.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}

        # Personal address - direct attribute access
        user.personal_street = data.get('personal_street')
        user.personal_city = data.get('personal_city')
        user.personal_postal_code = data.get('personal_postal_code')
        user.personal_country = data.get('personal_country')

        # Billing address - direct attribute access
        user.billing_street = data.get('billing_street')
        user.billing_city = data.get('billing_city')
        user.billing_postal_code = data.get('billing_postal_code')
        user.billing_country = data.get('billing_country')

        # GDPR consent
        if 'gdpr_consent' in data:
            user.gdpr_consent = bool(data['gdpr_consent'])
            if user.gdpr_consent:
                user.gdpr_consent_date = datetime.utcnow()
            else:
                user.gdpr_consent_date = None  # When withdrawing consent, also clear the date

        # Gender
        if 'gender' in data:
            gender_str = data['gender'].lower()
            if gender_str in ('male', 'female'):
                user.gender = Gender[gender_str.upper()]

        # Age
        if 'age' in data:
            try:
                user.age = int(data['age'])
            except (ValueError, TypeError):
                pass

        # Favorite genres
        if 'favorite_genres' in data:
            genre_names = data['favorite_genres']
            if isinstance(genre_names, list):
                # Find all existing genres by their names
                genres = Genre.query.filter(Genre.name.in_(genre_names)).all()

                # Create a dictionary for quick lookup of existing genres
                existing_genres = {genre.name: genre for genre in genres}

                # Create new genres for those that do not yet exist
                new_genres = []
                for name in genre_names:
                    if name not in existing_genres:
                        new_genre = Genre(name=name, is_active=True)
                        db.session.add(new_genre)
                        new_genres.append(new_genre)

                # Update user's favorite genres
                user.favorite_genres = list(existing_genres.values()) + new_genres

        # Referral source
        if 'referral_source' in data:
            user.referral_source = data['referral_source']

        # Role
        if 'role' in data and data['role'] in ('USER', 'ADMIN'):
            user.role = data['role']

        db.session.commit()

        return {
            'message': 'Profile successfully updated',
            'user': format_user_data(user)
        }

    except Exception as e:
        db.session.rollback()
        return {'error': f'Error updating profile: {str(e)}'}
