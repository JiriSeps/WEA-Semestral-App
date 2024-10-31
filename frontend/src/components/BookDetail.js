import React from 'react';

const BookDetail = ({ 
  isbn, 
  translations, 
  language, 
  onBackToList  // Nový prop
}) => {
  const [book, setBook] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const fetchBookDetail = async () => {
      try {
        const response = await fetch(`http://localhost:8007/api/books/${isbn}`);
        if (!response.ok) {
          throw new Error('Book not found');
        }
        const data = await response.json();
        setBook(data.book);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchBookDetail();
  }, [isbn]);

  if (loading) {
    return <div className="loading-message">{translations[language].loading}</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!book) {
    return <div className="not-found-message">{translations[language].bookNotFound}</div>;
  }

  return (
    <div className="book-detail-container">
      <button
        onClick={onBackToList}
        className="back-button"
      >
        {translations[language].back}
      </button>
      
      <div className="book-card">
        {/* Zbytek kódu zůstává stejný jako v původní verzi */}
        <div className="book-content">
          <div className="book-header">
            <h1 className="book-title">{book.Title}</h1>
            {book.Cover_Image && (
              <div className="book-cover-container">
                <img
                  src={book.Cover_Image}
                  alt={book.Title}
                  className="book-cover-image"
                  onError={(e) => {
                    e.target.src = '/placeholder-book.png';
                    e.target.onerror = null;
                  }}
                />
              </div>
            )}
            <h2 className="book-author">{book.Author}</h2>
            <div className="book-details-grid">
              <div>
                <p className="book-detail-label">{translations[language].isbn10}: {book.ISBN10 || '-'}</p>
              </div>
              <div>
                <p className="book-detail-label">{translations[language].isbn13}: {book.ISBN13 || '-'}</p>
              </div>
              <div>
                <p className="book-detail-label">{translations[language].yearOfPublication}: {book.Year_of_Publication || '-'}</p>
              </div>
              <div>
                <p className="book-detail-label">{translations[language].numberOfPages}: {book.Number_of_Pages || '-'}</p>
              </div>
              <div>
                <p className="book-detail-label">{translations[language].averageRating}: {book.Average_Customer_Rating?.toFixed(1) || '-'}</p>
              </div>
              <div>
                <p className="book-detail-label">{translations[language].numberOfRatings}: {book.Number_of_Ratings?.toLocaleString() || '-'}</p>
              </div>
            </div>
          </div>
          
          <div className="book-description-section">
            <div className="genres-container">
              <h3 className="genres-title">{translations[language].genres}</h3>
              <p className="genres-text">{book.Genres || '-'}</p>
            </div>
            
            {book.Description && (
              <div className="description-container">
                <h3 className="description-title">{translations[language].description}</h3>
                <p className="description-text">{book.Description}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookDetail;