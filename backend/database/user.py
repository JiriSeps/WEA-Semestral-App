from enum import Enum
from datetime import datetime
from . import db

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Osobní adresa
    personal_street = db.Column(db.String(200))
    personal_city = db.Column(db.String(100))
    personal_postal_code = db.Column(db.String(10))
    personal_country = db.Column(db.String(100))
    
    # Fakturační adresa
    billing_street = db.Column(db.String(200))
    billing_city = db.Column(db.String(100))
    billing_postal_code = db.Column(db.String(10))
    billing_country = db.Column(db.String(100))
    
    # Osobní údaje
    gdpr_consent = db.Column(db.Boolean, default=False, nullable=True)
    gdpr_consent_date = db.Column(db.DateTime, nullable=True)
    gender = db.Column(db.Enum(Gender), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    favorite_genres = db.relationship('Genre',
        secondary='user_favorite_genres',
        lazy='dynamic',
        backref=db.backref('users_who_favorite', lazy='dynamic')
    )
    referral_source = db.Column(db.String(200))

    # Vztah k oblíbeným knihám
    favorite_books = db.relationship('Book',
        secondary='favorite_books',
        lazy='dynamic',
        backref=db.backref('favorited_by', lazy='dynamic')
    )

    # Vztah ke košíku
    books_in_cart = db.relationship('Book',
        secondary='books_in_cart',
        lazy='dynamic',
        backref=db.backref('added_by', lazy='dynamic')
    )

    def __repr__(self):
        return f'<User {self.username}>'

# Vazební tabulka pro oblíbené knihy
favorite_books = db.Table('favorite_books',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('book_isbn10', db.String(10), db.ForeignKey('book.ISBN10'), primary_key=True),
    db.Column('added_at', db.DateTime, default=db.func.current_timestamp())
)

# Vazební tabulka pro košík
books_in_cart = db.Table('books_in_cart',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('book_isbn10', db.String(10), db.ForeignKey('book.ISBN10'), primary_key=True),
    db.Column('added_at', db.DateTime, default=db.func.current_timestamp())
)

# Vazební tabulka pro oblíbené žánry
user_favorite_genres = db.Table('user_favorite_genres',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True),
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)