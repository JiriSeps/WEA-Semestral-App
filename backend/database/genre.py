from datetime import datetime
from . import db

class Genre(db.Model):
    """
    Genre model representing a category of items such as books, movies, or music.

    Attributes:
        id (int): The primary key for the genre.
        name (str): The name of the genre, which must be unique and non-nullable.
        created_at (datetime): The timestamp when the genre was created, defaults to the current UTC time.
        is_active (bool): Indicates whether the genre is active, defaults to True.
    
    Methods:
        __repr__(): Returns a string representation of the Genre instance.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Genre {self.name}>'
