import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

const translations = {
  cs: {
    title: "Knihkupectví",
    cover: "Náhled",
    searchBook: "Název knihy:",
    searchAuthor: "Autor (autoři odděleni čárkou):",
    searchISBN: "ISBN:",
    search: "Hledat",
    clearSearch: "Zrušit vyhledávání",
    loading: "Načítání...",
    error: "Nepodařilo se načíst knihy. Prosím, zkuste to znovu později.",
    noResults: "Žádné knihy nenalezeny.",
    previous: "Předchozí",
    next: "Další",
    genres: "Žánry",
    page: "Stránka:",
    of: "z"
  },
  en: {
    title: "Book Store",
    cover: "Cover",
    searchBook: "Book Title:",
    searchAuthor: "Author(s) separated by comma:",
    searchISBN: "ISBN:",
    search: "Search",
    clearSearch: "Clear Search",
    loading: "Loading...",
    error: "Failed to load books. Please try again later.",
    noResults: "No books found.",
    previous: "Previous",
    next: "Next",
    genres: "Genres",
    page: "Page:",
    of: "of"
  }
};

function App() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [searchQueries, setSearchQueries] = useState({
    title: '',
    author: '',
    isbn: ''
  });
  const [currentSearchQueries, setCurrentSearchQueries] = useState({
    title: '',
    author: '',
    isbn: ''
  });
  const [language, setLanguage] = useState('cs');

  useEffect(() => {
    fetchBooks(currentPage, currentSearchQueries);
  }, [currentPage, currentSearchQueries]);

  const fetchBooks = (page, queries) => {
    setLoading(true);
    const queryParams = new URLSearchParams({
      page: page,
      per_page: 25,
      title: queries.title,
      author: queries.author,
      isbn: queries.isbn
    });

    axios.get(`http://localhost:8007/api/books?${queryParams.toString()}`)
      .then(response => {
        setBooks(response.data.books);
        setTotalPages(response.data.total_pages);
        setLoading(false);
      })
      .catch(error => {
        console.error("There was an error fetching the books!", error);
        setError(translations[language].error); // Použij překlad
        setLoading(false);
      });
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  const handleSearchChange = (field) => (event) => {
    setSearchQueries(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    setCurrentSearchQueries(searchQueries);
    setCurrentPage(1);
  };

  const handleClearSearch = () => {
    setSearchQueries({
      title: '',
      author: '',
      isbn: ''
    });
    setCurrentSearchQueries({
      title: '',
      author: '',
      isbn: ''
    });
    setCurrentPage(1);
  };

  const toggleLanguage = () => {
    setLanguage(prev => (prev === 'cs' ? 'en' : 'cs')); // Přepínání jazyka
  };

  if (loading) return (
    <div className="loading-container">
      <div className="loading">{translations[language].loading}</div>
    </div>
  );

  if (error) return (
    <div className="error-container">
      <div className="error">{error}</div>
    </div>
  );

  return (
    <div className="App">
      <div className="header">
        <button onClick={toggleLanguage} className="language-toggle">
          {language === 'cs' ? 'EN' : 'CS'} {/* Změna textu tlačítka */}
        </button>
        <h1>{translations[language].title}</h1>
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
      </div>

      {books.length > 0 ? (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>{translations[language].cover}</th>
                  <th>{translations[language].searchBook}</th>
                  <th>{translations[language].searchAuthor}</th>
                  <th>ISBN10</th>
                  <th>ISBN13</th>
                  <th>{translations[language].genres}</th>
                  <th>{translations[language].yearOfPublication}</th>
                  <th>{translations[language].numberOfPages}</th>
                  <th>{translations[language].averageRating}</th>
                  <th>{translations[language].numberOfRatings}</th>
                </tr>
              </thead>
              <tbody>
                {books.map(book => (
                  <tr key={book.ISBN10 || book.ISBN13}>
                    <td>
                      {book.Cover_Image && (
                        <img 
                          src={book.Cover_Image} 
                          alt={book.Title} 
                          className="book-cover"
                          onError={(e) => {
                            e.target.src = '/placeholder-book.png';
                            e.target.onerror = null;
                          }}
                        />
                      )}
                    </td>
                    <td>{book.Title}</td>
                    <td>{book.Author}</td>
                    <td>{book.ISBN10}</td>
                    <td>{book.ISBN13}</td>
                    <td>{book.Genres}</td>
                    <td>{book.Year_of_Publication}</td>
                    <td>{book.Number_of_Pages}</td>
                    <td>{book.Average_Customer_Rating?.toFixed(1)}</td>
                    <td>{book.Number_of_Ratings}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="pagination">
            <button 
              onClick={() => handlePageChange(currentPage - 1)} 
              disabled={currentPage === 1}
              className="pagination-button"
            >
              {translations[language].previous}
            </button>
            <span className="page-info">{translations[language].page} {currentPage} {translations[language].of} {totalPages}</span>
            <button 
              onClick={() => handlePageChange(currentPage + 1)} 
              disabled={currentPage === totalPages}
              className="pagination-button"
            >
              {translations[language].next}
            </button>
          </div>
        </>
      ) : (
        <div className="no-results">{translations[language].noResults}</div>
      )}
    </div>
  );
}

export default App;
