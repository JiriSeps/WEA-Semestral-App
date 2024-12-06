import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

export const SearchForm = ({ 
  searchQueries, 
  handleSearchChange, 
  handleSearchSubmit, 
  handleClearSearch, 
  currentSearchQueries, 
  translations, 
  language,
  showFavorites,  // nový prop
  onToggleFavorites,  // nový prop
  user  // nový prop pro kontrolu, zda je uživatel přihlášený
}) => {
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isGenresOpen, setIsGenresOpen] = useState(false);

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/genres`);
        setGenres(response.data.genres);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching genres:", error);
        setLoading(false);
      }
    };

    fetchGenres();
  }, []);

  const handleGenreChange = (genre) => {
    const currentGenres = searchQueries.genres || [];
    const updatedGenres = currentGenres.includes(genre)
      ? currentGenres.filter(g => g !== genre)
      : [...currentGenres, genre];
    
    handleSearchChange('genres')({ target: { value: updatedGenres } });
  };

  const toggleGenres = () => {
    setIsGenresOpen(!isGenresOpen);
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSearchSubmit}>
        <div className="view-toggle">
          <button
            type="button"
            className={`view-button ${!showFavorites ? 'active' : ''}`}
            onClick={() => onToggleFavorites(false)}
          >
            {translations[language].allBooks}
          </button>
          {user && (
            <button
              type="button"
              className={`view-button ${showFavorites ? 'active' : ''}`}
              onClick={() => onToggleFavorites(true)}
            >
              {translations[language].favoriteBooks}
            </button>
          )}
        </div>
        <div className="search-fields">
          <div className="search-field">
            <label>{translations[language].searchBook}</label>
            <input
              type="text"
              placeholder={translations[language].searchBook}
              value={searchQueries.title}
              onChange={handleSearchChange('title')}
              className="search-input"
            />
          </div>
          <div className="search-field">
            <label>{translations[language].searchAuthor}</label>
            <input
              type="text"
              placeholder={translations[language].searchAuthor}
              value={searchQueries.author}
              onChange={handleSearchChange('author')}
              className="search-input"
            />
          </div>
          <div className="search-field">
            <label>{translations[language].searchISBN}</label>
            <input
              type="text"
              placeholder={translations[language].searchISBN}
              value={searchQueries.isbn}
              onChange={handleSearchChange('isbn')}
              className="search-input"
            />
          </div>
          <div className="genres-field">
          <label>{translations[language].genres}</label>
            <button 
              type="button" 
              className="genres-dropdown-button" 
              onClick={toggleGenres}
            >
              {translations[language].genres} 
              ({(searchQueries.genres || []).length} {translations[language].selected})
              <span className={`arrow ${isGenresOpen ? 'up' : 'down'}`}>▼</span>
            </button>
            {isGenresOpen && !loading && (
              <div className="genres-dropdown">
                {genres.map(genre => (
                  <label key={genre} className="genre-checkbox">
                    <input
                      type="checkbox"
                      checked={(searchQueries.genres || []).includes(genre)}
                      onChange={() => handleGenreChange(genre)}
                    />
                    <span>{genre}</span>
                  </label>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="search-buttons">
          <button type="submit" className="search-button">
            {translations[language].search}
          </button>
          {(currentSearchQueries.title || 
            currentSearchQueries.author || 
            currentSearchQueries.isbn ||
            (currentSearchQueries.genres && currentSearchQueries.genres.length > 0)) && (
            <button type="button" onClick={handleClearSearch} className="clear-button">
              {translations[language].clearSearch}
            </button>
          )}
        </div>
      </form>
    </div>
  );
};