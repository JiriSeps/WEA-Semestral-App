from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    
    ISBN10 = db.Column(db.String(10), primary_key=True)
    ISBN13 = db.Column(db.String(13), unique=True, nullable=False)
    Title = db.Column(db.String(255), nullable=False)
    Author = db.Column(db.String(255), nullable=False)
    Genres = db.Column(db.String(255))
    Cover_Image = db.Column(db.String(255))
    Critics_Rating = db.Column(db.Float)
    Year_of_Publication = db.Column(db.Integer)
    Number_of_Pages = db.Column(db.Integer)
    Average_Customer_Rating = db.Column(db.Float)
    Number_of_Ratings = db.Column(db.Integer)
