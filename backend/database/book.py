from . import db

class Book(db.Model):
    """
    Represents a book in the database with comprehensive book information.

    This model captures detailed metadata about a book, including its 
    identification, publication details, and various rating and visibility attributes.

    Attributes:
        ISBN10 (str): 10-digit International Standard Book Number (primary key)
        ISBN13 (str): 13-digit International Standard Book Number
        Title (str): The title of the book
        Author (str): The author or authors of the book
        Cover_Image (str, optional): URL or path to the book's cover image
        Description (str, optional): Detailed description or synopsis of the book
        Year_of_Publication (int, optional): The year the book was published
        Number_of_Pages (int, optional): Total number of pages in the book
        Average_Rating (float, optional): Aggregate user rating for the book
        Number_of_Ratings (int, optional): Total number of ratings received
        Price (float, optional): Current price of the book
        is_visible (bool): Indicates whether the book is visible in the catalog (default: True)

    Relationships:
        - genres: Dynamic relationship with Genre model through book_genres association table
        - comments: Relationship with Comment model, allowing access to book's comments

    Example:
        book = Book(
            ISBN10='1234567890', 
            ISBN13='1234567890123', 
            Title='Sample Book', 
            Author='John Doe',
            Year_of_Publication=2023
        )
    """
    ISBN10 = db.Column(db.String(10), primary_key=True)
    ISBN13 = db.Column(db.String(13), unique=True, nullable=False)
    Title = db.Column(db.String(255), nullable=False)
    Author = db.Column(db.String(255), nullable=False)
    Cover_Image = db.Column(db.String(255))
    Description = db.Column(db.Text)
    Year_of_Publication = db.Column(db.Integer)
    Number_of_Pages = db.Column(db.Integer)
    Average_Rating = db.Column(db.Float)
    Number_of_Ratings = db.Column(db.Integer)
    Price = db.Column(db.Float)
    is_visible = db.Column(db.Boolean, default=True)

    # Vztah k žánrům
    genres = db.relationship('Genre',
        secondary='book_genres',
        lazy='dynamic',
        backref=db.backref('books', lazy='dynamic')
    )

    # Vztah k komentářům
    comments = db.relationship('Comment', backref='book', lazy=True)

    def __repr__(self):
        """
        Provides a string representation of the Book instance.

        Returns:
            str: A string containing the book's title
        """
        return f'<Book {self.Title}>'

# Vazební tabulka pro žánry knih
book_genres = db.Table('book_genres',
    db.Column('book_isbn10', db.String(10), db.ForeignKey('book.ISBN10'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)
