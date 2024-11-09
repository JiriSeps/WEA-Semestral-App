from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Vztah k oblíbeným knihám
    favorite_books = db.relationship('Book',
        secondary='favorite_books',
        lazy='dynamic',
        backref=db.backref('favorited_by', lazy='dynamic')
    )

    def __repr__(self):
        return f'<User {self.username}>'

# Vazební tabulka pro oblíbené knihy
favorite_books = db.Table('favorite_books',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('book_isbn10', db.String(10), db.ForeignKey('book.ISBN10'), primary_key=True),
    db.Column('added_at', db.DateTime, default=db.func.current_timestamp())
)