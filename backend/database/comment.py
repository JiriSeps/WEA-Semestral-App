from datetime import datetime
from . import db

class Comment(db.Model):
    """
    Represents a user comment associated with a specific book in the database.

    This model captures user-generated comments, tracking the comment text, 
    creation timestamp, and the associated book and user.

    Attributes:
        id (int): Unique identifier for the comment (primary key)
        text (str): The content of the comment (required)
        created_at (datetime): Timestamp of when the comment was created 
                                (defaults to current UTC time)
        book_isbn (str): ISBN of the book the comment is associated with
        user_id (int): Identifier of the user who created the comment

    Relationships:
        - Linked to Book model via book_isbn foreign key
        - Linked to User model via user_id foreign key

    Example:
        comment = Comment(
            text='Great book! Highly recommended.',
            book_isbn='1234567890', 
            user_id=123
        )
    """
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Cizí klíče
    book_isbn = db.Column(db.String(10), db.ForeignKey('book.ISBN10'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        """
        Provides a string representation of the Comment instance.

        Returns:
            str: A string containing the comment's ID and associated book's ISBN
        """
        return f'<Comment {self.id} for book {self.book_isbn}>'
