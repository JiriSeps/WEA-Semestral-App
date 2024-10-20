import React from 'react';

export const SearchForm = ({ searchQueries, handleSearchChange, handleSearchSubmit, handleClearSearch, currentSearchQueries, translations, language }) => (
  <div className="search-container">
    <form onSubmit={handleSearchSubmit}>
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
      </div>
      <div className="search-buttons">
        <button type="submit" className="search-button">{translations[language].search}</button>
        {(currentSearchQueries.title || currentSearchQueries.author || currentSearchQueries.isbn) && (
          <button type="button" onClick={handleClearSearch} className="clear-button">
            {translations[language].clearSearch}
          </button>
        )}
      </div>
    </form>
  </div>
);