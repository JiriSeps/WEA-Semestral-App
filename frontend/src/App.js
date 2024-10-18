import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

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
        setError("Nepodařilo se načíst knihy. Prosím, zkuste to znovu později.");
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

  if (loading) return (
    <div className="loading-container">
      <div className="loading">Načítání...</div>
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
        <h1>Seznam knih</h1>
        <div className="search-container">
          <form onSubmit={handleSearchSubmit}>
            <div className="search-fields">
              <div className="search-field">
                <label>Název knihy:</label>
                <input
                  type="text"
                  placeholder="Zadejte název knihy..."
                  value={searchQueries.title}
                  onChange={handleSearchChange('title')}
                  className="search-input"
                />
              </div>
              <div className="search-field">
                <label>Autor (autoři oddělení čárkou):</label>
                <input
                  type="text"
                  placeholder="Zadejte autora/autory..."
                  value={searchQueries.author}
                  onChange={handleSearchChange('author')}
                  className="search-input"
                />
              </div>
              <div className="search-field">
                <label>ISBN:</label>
                <input
                  type="text"
                  placeholder="Zadejte ISBN10 nebo ISBN13..."
                  value={searchQueries.isbn}
                  onChange={handleSearchChange('isbn')}
                  className="search-input"
                />
              </div>
            </div>
            <div className="search-buttons">
              <button type="submit" className="search-button">Hledat</button>
              {(currentSearchQueries.title || currentSearchQueries.author || currentSearchQueries.isbn) && (
                <button type="button" onClick={handleClearSearch} className="clear-button">
                  Zrušit vyhledávání
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
                  <th>Obrázek</th>
                  <th>Název</th>
                  <th>Autor</th>
                  <th>ISBN10</th>
                  <th>ISBN13</th>
                  <th>Žánry</th>
                  <th>Rok vydání</th>
                  <th>Počet stran</th>
                  <th>Průměrné hodnocení</th>
                  <th>Počet hodnocení</th>
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
              Předchozí
            </button>
            <span className="page-info">Stránka {currentPage} z {totalPages}</span>
            <button 
              onClick={() => handlePageChange(currentPage + 1)} 
              disabled={currentPage === totalPages}
              className="pagination-button"
            >
              Další
            </button>
          </div>
        </>
      ) : (
        <div className="no-results">Žádné knihy nenalezeny.</div>
      )}
    </div>
  );
}

export default App;