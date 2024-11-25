from . import db

class Book(db.Model):
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
        return f'<Book {self.Title}>'

# Vazební tabulka pro žánry knih
book_genres = db.Table('book_genres',
    db.Column('book_isbn10', db.String(10), db.ForeignKey('book.ISBN10'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)