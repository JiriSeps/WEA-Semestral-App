from database.user import db, User
from werkzeug.security import generate_password_hash, check_password_hash

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