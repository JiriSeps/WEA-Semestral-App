# genre_operations.py
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from .genre import Genre
from .book import Book, book_genres
from . import db

def filter_books_by_genres(query, genres_string):
    """
    Filtruje knihy podle zadaných žánrů.
    
    Args:
        query: Existující SQLAlchemy query object s knihami
        genres_string: String se žánry oddělenými středníkem
    
    Returns:
        SQLAlchemy query objekt s přidaným filtrem na žánry
    """
    if not genres_string:
        return query
        
    genre_terms = [genre.strip() for genre in genres_string.split(';') if genre.strip()]
    
    if not genre_terms:
        return query
    
    # Pro každý žánr najdeme odpovídající Genre záznamy
    for genre_term in genre_terms:
        # Najdeme žánry, které odpovídají hledanému termínu
        matching_genres = Genre.query.filter(Genre.name.ilike(f'%{genre_term}%')).all()
        if matching_genres:
            # Vytvoříme seznam ID nalezených žánrů
            genre_ids = [genre.id for genre in matching_genres]
            # Filtrujeme knihy, které mají vazbu na některý z těchto žánrů
            query = query.join(book_genres).filter(book_genres.c.genre_id.in_(genre_ids))
    
    return query

def get_or_create_genres(genres_string):
    """
    Získá nebo vytvoří žánry z textového řetězce.
    
    Args:
        genres_string: String s žánry oddělenými čárkou nebo středníkem
    
    Returns:
        List objektů Genre
    """
    if not genres_string:
        return []
        
    # Rozdělíme string na jednotlivé žánry a očistíme je
    genre_names = [name.strip() for name in genres_string.replace(';', ',').split(',')]
    genre_names = [name for name in genre_names if name]  # Odstraníme prázdné stringy
    
    genres = []
    for name in genre_names:
        # Pro každý název žánru se pokusíme najít existující nebo vytvořit nový
        genre = Genre.query.filter(Genre.name.ilike(name)).first()
        if not genre:
            genre = Genre(name=name, is_active=True)
            db.session.add(genre)
        genres.append(genre)
    
    return genres

def update_book_genres(book, genres_string):
    """
    Aktualizuje žánry knihy.
    
    Args:
        book: Instance Book modelu
        genres_string: String s žánry oddělenými čárkou nebo středníkem
    """
    # Získáme nebo vytvoříme žánry
    genres = get_or_create_genres(genres_string)
    
    # Aktualizujeme vazby knihy na žánry
    book.genres = genres


def get_all_unique_genres():
    """
    Získá všechny unikátní žánry z aktivních knih.
    
    Returns:
        List[str]: Seřazený seznam názvů žánrů
    """
    try:
        # Získáme všechny žánry, které mají alespoň jednu viditelnou knihu
        active_genres = Genre.query\
            .join(book_genres)\
            .join(Book)\
            .filter(Book.is_visible == True)\
            .distinct()\
            .order_by(Genre.name)\
            .all()
        
        # Vrátíme seřazený seznam názvů žánrů
        return [genre.name for genre in active_genres]
    except SQLAlchemyError as e:
        print(f"Error getting unique genres: {str(e)}")
        return []