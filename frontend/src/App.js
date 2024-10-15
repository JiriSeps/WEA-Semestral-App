import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentSearchQuery, setCurrentSearchQuery] = useState('');

  useEffect(() => {
    fetchBooks(currentPage, currentSearchQuery);
  }, [currentPage, currentSearchQuery]);

  const fetchBooks = (page, query) => {
    setLoading(true);
    axios.get(`http://localhost:8007/api/books?page=${page}&per_page=25&search=${query}`)
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

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    setCurrentSearchQuery(searchQuery);
    setCurrentPage(1);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setCurrentSearchQuery('');
    setCurrentPage(1);
  };

  if (loading) return <div className="loading">Načítání...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="App">
      <div className="header">
        <h1>Seznam knih</h1>
        <div className="search-container">
          <form onSubmit={handleSearchSubmit}>
            <input
              type="text"
              placeholder="Vyhledat knihy nebo autory..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="search-input"
            />
            <button type="submit" className="search-button">Hledat</button>
            {currentSearchQuery && (
              <button type="button" onClick={handleClearSearch} className="clear-button">
                Zrušit vyhledávání
              </button>
            )}
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
                  <tr key={book.ISBN10}>
                    <td><img src={book.Cover_Image} alt={book.Title} /></td>
                    <td>{book.Title}</td>
                    <td>{book.Author}</td>
                    <td>{book.ISBN10}</td>
                    <td>{book.ISBN13}</td>
                    <td>{book.Genres}</td>
                    <td>{book.Year_of_Publication}</td>
                    <td>{book.Number_of_Pages}</td>
                    <td>{book.Average_Customer_Rating}</td>
                    <td>{book.Number_of_Ratings}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="pagination">
            <button onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>
              Předchozí
            </button>
            <span>Stránka {currentPage} z {totalPages}</span>
            <button onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === totalPages}>
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