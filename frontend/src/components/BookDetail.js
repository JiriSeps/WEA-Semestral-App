import React, { useState, useEffect } from 'react';
import BookComments from './BookComments';

const BookDetail = ({ 
  isbn, 
  translations, 
  language, 
  onBackToList,
  user
}) => {
  const [book, setBook] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  const [isFavoriteLoading, setIsFavoriteLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  React.useEffect(() => {
    const fetchBookDetail = async () => {
      try {
        const response = await fetch(`http://localhost:8007/api/books/${isbn}`, {
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error(translations[language].bookNotFound);
        }
        
        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }
        
        setBook(data.book);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchBookDetail();
  }, [isbn, language]);

  const toggleFavorite = async () => {
    if (!user) {
      setStatusMessage({
        type: 'error',
        text: translations[language].loginRequired
      });
      return;
    }

    setIsFavoriteLoading(true);
    try {
      const response = await fetch(`http://localhost:8007/api/favorites/${isbn}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || translations[language].favoriteError);
      }

      setBook(prev => ({
        ...prev,
        is_favorite: !prev.is_favorite
      }));
      
      setStatusMessage({
        type: 'success',
        text: data.message || (book.is_favorite 
          ? translations[language].removedFromFavorites 
          : translations[language].addedToFavorites)
      });
      
    } catch (err) {
      setStatusMessage({
        type: 'error',
        text: err.message
      });
    } finally {
      setIsFavoriteLoading(false);
      // Clear status message after 3 seconds
      setTimeout(() => setStatusMessage(null), 3000);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="loading-message">{translations[language].loading}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="error-message text-red-500">{error}</div>
      </div>
    );
  }

  if (!book) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="not-found-message">{translations[language].bookNotFound}</div>
      </div>
    );
  }

  return (
    <div className="book-detail-container">
      <button
        onClick={onBackToList}
        className="back-button mb-4 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded"
      >
        {translations[language].back}
      </button>

      {statusMessage && (
        <div className={`mb-4 p-4 rounded ${
          statusMessage.type === 'error' 
            ? 'bg-red-100 text-red-700' 
            : 'bg-green-100 text-green-700'
        }`}>
          {statusMessage.text}
        </div>
      )}

      <div className="book-card bg-white shadow-lg rounded-lg p-6">
        <div className="book-content">
          <div className="book-header">
            <div className="flex items-center justify-between mb-4">
              <h1 className="book-title text-2xl font-bold">{book.Title}</h1>
              {user && (
                <button 
                  onClick={toggleFavorite}
                  disabled={isFavoriteLoading}
                  className={`favorite-button p-2 rounded-full transition-colors ${
                    book.is_favorite 
                      ? 'bg-red-100 hover:bg-red-200' 
                      : 'bg-gray-100 hover:bg-gray-200'
                  } ${isFavoriteLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  aria-label={book.is_favorite ? translations[language].removeFromFavorites : translations[language].addToFavorites}
                >
                  <span className={`text-2xl ${book.is_favorite ? 'text-red-500' : 'text-gray-400'}`}>
                    {book.is_favorite ? '❤️' : '🤍'}
                  </span>
                </button>
              )}
            </div>
            
            {book.Cover_Image && (
              <div className="book-cover-container mb-4">
                <img
                  src={book.Cover_Image}
                  alt={book.Title}
                  className="book-cover-image max-w-xs mx-auto rounded shadow"
                  onError={(e) => {
                    e.target.src = '/placeholder-book.png';
                    e.target.onerror = null;
                  }}
                />
              </div>
            )}
            <h2 className="book-author text-xl text-gray-700 mb-4">{book.Author}</h2>
            
            <div className="book-details-grid grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              <div>
                <p className="book-detail-label">
                  <span className="font-medium">{translations[language].isbn10}:</span> {book.ISBN10 || '-'}
                </p>
              </div>
              <div>
                <p className="book-detail-label">
                  <span className="font-medium">{translations[language].isbn13}:</span> {book.ISBN13 || '-'}
                </p>
              </div>
              <div>
                <p className="book-detail-label">
                  <span className="font-medium">{translations[language].yearOfPublication}:</span> {book.Year_of_Publication || '-'}
                </p>
              </div>
              <div>
                <p className="book-detail-label">
                  <span className="font-medium">{translations[language].numberOfPages}:</span> {book.Number_of_Pages || '-'}
                </p>
              </div>
              <div>
                <p className="book-detail-label">
                  <span className="font-medium">{translations[language].averageRating}:</span> {book.Average_Customer_Rating?.toFixed(1) || '-'}
                </p>
              </div>
              <div>
                <p className="book-detail-label">
                  <span className="font-medium">{translations[language].numberOfRatings}:</span> {book.Number_of_Ratings?.toLocaleString() || '-'}
                </p>
              </div>
            </div>
          </div>

          <div className="book-description-section">
            <div className="genres-container mb-4">
              <h3 className="genres-title text-lg font-medium mb-2">{translations[language].genres}</h3>
              <p className="genres-text">{book.Genres || '-'}</p>
            </div>

            {book.Description && (
              <div className="description-container">
                <h3 className="description-title text-lg font-medium mb-2">{translations[language].description}</h3>
                <p className="description-text">{book.Description}</p>
              </div>
            )}
          </div>
        </div>
        
        <BookComments 
          isbn={book.ISBN10} 
          translations={translations} 
          language={language}
          user={user}
        />
      </div>
    </div>
  );
};

export default BookDetail;