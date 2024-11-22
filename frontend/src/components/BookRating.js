import React, { useState, useEffect } from 'react';
import { Star } from 'lucide-react';

const BookRating = ({ isbn, user, translations, language, onRatingUpdate, currentRating }) => {
  const [userRating, setUserRating] = useState(currentRating || null);
  const [hoveredRating, setHoveredRating] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusMessage, setStatusMessage] = useState(null);

  useEffect(() => {
    setUserRating(currentRating || null);
  }, [currentRating]);

  useEffect(() => {
    if (user && !currentRating) {
      fetchUserRating();
    } else {
      setLoading(false);
    }
  }, [isbn, user, currentRating]);

  const fetchUserRating = async () => {
    try {
      const response = await fetch(`http://localhost:8007/api/ratings/${isbn}`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error(translations[language].ratingFetchError);
      }
      
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      
      setUserRating(data.rating);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRating = async (rating) => {
    if (!user) {
      setStatusMessage({
        type: 'error',
        text: translations[language].loginRequired
      });
      return;
    }

    try {
      const response = await fetch(`http://localhost:8007/api/ratings/${isbn}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rating })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || translations[language].ratingError);
      }

      setUserRating(rating);
      if (onRatingUpdate) {
        onRatingUpdate();
      }
      
      setStatusMessage({
        type: 'success',
        text: translations[language].ratingSuccess
      });
      
    } catch (err) {
      setStatusMessage({
        type: 'error',
        text: err.message
      });
    }

    setTimeout(() => setStatusMessage(null), 3000);
  };

  if (loading) {
    return <div>{translations[language].loading}</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div className="rating-container">
      {statusMessage && (
        <div className={`mb-4 p-4 rounded ${
          statusMessage.type === 'error' 
            ? 'bg-red-100 text-red-700' 
            : 'bg-green-100 text-green-700'
        }`}>
          {statusMessage.text}
        </div>
      )}
      
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((rating) => (
          <button
            key={rating}
            onClick={() => handleRating(rating)}
            onMouseEnter={() => setHoveredRating(rating)}
            onMouseLeave={() => setHoveredRating(null)}
            className={`p-1 transition-colors ${
              !user ? 'cursor-not-allowed opacity-50' : 'hover:bg-gray-100'
            }`}
            disabled={!user}
          >
            <Star
              size={24}
              className={`transition-colors`}
              fill={hoveredRating ? rating <= hoveredRating : rating <= (userRating || 0) ? '#facc15' : 'none'}
              stroke={hoveredRating ? rating <= hoveredRating : rating <= (userRating || 0) ? '#facc15' : '#d1d5db'}
            />
          </button>
        ))}
      </div>
      
      {!user && (
        <p className="text-sm text-gray-500 mt-2">
          {translations[language].loginToRate}
        </p>
      )}
    </div>
  );
};

export default BookRating;