from datetime import datetime
from . import db

class Rating(db.Model):
    """
    Rating model representing a user's rating for a specific book.

    Attributes:
        id (int): The primary key for the rating.
        user_id (int): The ID of the user .
        book_isbn (str): The ISBN-13 of the book being rated, linked to the book table.
        rating (int): The rating score provided by the user.
        created_at (datetime): The timestamp when the rating was created.

    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_isbn = db.Column(db.String(13), db.ForeignKey('book.ISBN13'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_isbn', name='unique_user_book_rating'),
    )
