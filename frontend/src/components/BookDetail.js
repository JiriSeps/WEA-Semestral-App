import React, { useState, useEffect } from 'react';
import BookComments from './BookComments';
import BookRating from './BookRating';

const BookDetail = ({ 
  isbn, 
  translations, 
  language, 
  onBackToList,
  user
}) => {
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFavoriteLoading, setIsFavoriteLoading] = useState(false);
  const [isCartLoading, setIsCartLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [isInCart, setIsInCart] = useState(false);

  const fetchBookDetail = async () => {
    try {
      setLoading(true);
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
      
      if (user) {
        await checkCartStatus();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
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
      setTimeout(() => setStatusMessage(null), 3000);
    }
  };

  const checkCartStatus = async () => {
    try {
      const response = await fetch(`http://localhost:8007/api/shoppingcart/${isbn}/status`, {
        credentials: 'include'
      });
      
      const data = await response.json();
      setIsInCart(data.is_favorite);
    } catch (err) {
      console.error('Failed to check cart status:', err);
    }
  };

  useEffect(() => {
    fetchBookDetail();
  }, [isbn, language]);

  const toggleCart = async () => {
    if (!user) {
      setStatusMessage({
        type: 'error',
        text: translations[language].loginRequired
      });
      return;
    }

    setIsCartLoading(true);
    try {
      const response = await fetch(`http://localhost:8007/api/shoppingcart/${isbn}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || translations[language].cartError);
      }

      setIsInCart(prev => !prev);
      
      setStatusMessage({
        type: 'success',
        text: data.message || (isInCart 
          ? translations[language].removedFromCart 
          : translations[language].addedToCart)
      });
      
    } catch (err) {
      setStatusMessage({
        type: 'error',
        text: err.message
      });
    } finally {
      setIsCartLoading(false);
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
        className="back-button"
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

      <div className="book-card">
        <div className="book-content">
          <div className="book-header">
          <div className="flex items-center space-x-2">
                {user && (
                  <>
                    <button 
                      onClick={toggleCart}
                      disabled={isCartLoading}
                      className={`cart-button ${
                        isInCart 
                          ? 'bg-green-100 hover:bg-green-200' 
                          : 'bg-gray-100 hover:bg-gray-200'
                      } ${isCartLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                      aria-label={isInCart ? translations[language].removeFromCart : translations[language].addToCart}
                    >
                      <span className={`text-2xl ${isInCart ? 'text-green-500' : 'text-gray-400'}`}>
                        🛒
                      </span>
                    </button>
                    <button 
                      onClick={toggleFavorite}
                      disabled={isFavoriteLoading}
                      className={`favorite-button ${
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
                  </>
                )}
              </div>
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
                <p className="book-detail-label">
                  <span className="font-medium">{translations[language].price}:</span> {book.Price || '-'}
                </p>
              </div>
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
                  <span className="font-medium">{translations[language].averageRating}:</span> {book.Average_Rating?.toFixed(1) || '-'}
                </p>
              </div>
              <div>
                <p className="book-detail-label">
                  <span className="font-medium">{translations[language].numberOfRatings}:</span> {book.Number_of_Ratings?.toLocaleString() || '-'}
                </p>
              </div>
            </div>
          </div>

          <div className="book-rating-section">
            <h3 className="text-lg font-medium">
              {translations[language].yourRating}
            </h3>
            <BookRating 
              isbn={book.ISBN10} 
              user={user}
              translations={translations}
              language={language}
              onRatingUpdate={fetchBookDetail}
            />
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