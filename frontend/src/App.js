import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Header } from './components/Header';
import { SearchForm } from './components/SearchForm';
import { BookList } from './components/BookList';
import { Pagination } from './components/Pagination';
import { translations } from './components/Translations';
import BookDetail from './components/BookDetail';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import ProfileForm from './components/ProfileForm';
import ShoppingCart from './components/ShoppingCart';
import OrderList from './components/UserOrders';  // Přidán import
import AuditLog from './components/AuditLog';
import { API_BASE_URL } from './config';

import './App.css';
axios.defaults.withCredentials = true; 

function App() {
  // Stavové proměnné
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [searchQueries, setSearchQueries] = useState({
    title: '',
    author: '',
    isbn: '',
    genres: []
  });
  const [currentSearchQueries, setCurrentSearchQueries] = useState({
    title: '',
    author: '',
    isbn: '',
    genres: []
  });
  const [language, setLanguage] = useState('cs');
  const [user, setUser] = useState(null);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [currentView, setCurrentView] = useState('list');
  const [selectedBookIsbn, setSelectedBookIsbn] = useState(null);
  const [showFavorites, setShowFavorites] = useState(false);
  const [showProfileForm, setShowProfileForm] = useState(false);
  const [showShoppingCart, setShowShoppingCart] = useState(false);
  const [showOrders, setShowOrders] = useState(false);  // Přidán nový state
  const [showAuditLog, setShowAuditLog] = useState(false);

  // Efekty
  useEffect(() => {
    fetchBooks(currentPage, currentSearchQueries);
    checkLoggedInUser();
  }, [currentPage, currentSearchQueries, showFavorites]);

  // API volání
  const fetchBooks = (page, queries) => {
    setLoading(true);
    const queryParams = new URLSearchParams({
      page: page,
      per_page: 25,
      title: queries.title,
      author: queries.author,
      isbn: queries.isbn,
      genres: queries.genres ? queries.genres.join(';') : '',
      favorites: showFavorites
    });
  
    axios.get(`${API_BASE_URL}/api/books?${queryParams.toString()}`)
      .then(response => {
        setBooks(response.data.books);
        setTotalPages(response.data.total_pages);
        setLoading(false);
      })
      .catch(error => {
        console.error("There was an error fetching the books!", error);
        setError(translations[language].error);
        setLoading(false);
      });
  };

  const checkLoggedInUser = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/user`);
      setUser(response.data.user);
    } catch (error) {
      console.error("Error checking logged in user", error);
      setShowFavorites(false);
    }
  };

  const toggleAuditLog = () => setShowAuditLog(prev => !prev);

  // Handlery
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  const handleProfileUpdate = (updatedUser) => {
    setUser(updatedUser);
    setShowProfileForm(false);
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
      isbn: '',
      genres: []
    });
    setCurrentSearchQueries({
      title: '',
      author: '',
      isbn: '',
      genres: []
    });
    setCurrentPage(1);
  };

  const handleToggleFavorites = (showFav) => {
    setShowFavorites(showFav);
    setCurrentPage(1);
    handleClearSearch();
  };

  const toggleLanguage = () => {
    setLanguage(prev => (prev === 'cs' ? 'en' : 'cs'));
  };

  const handleLogin = async (userData) => {
    try {
      setUser(userData);
      const response = await axios.get(`${API_BASE_URL}/api/user`);
      setUser(response.data.user);
      setShowLoginForm(false);
      setShowRegisterForm(false);
    } catch (error) {
      console.error("Error fetching complete user data", error);
    }
  };

  const handleRegister = () => {
    setShowRegisterForm(false);
    setShowLoginForm(true);
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/logout`);
      setUser(null);
      setShowFavorites(false);
      setShowAuditLog(false);
    } catch (error) {
      console.error("Error logging out", error);
    }
  };

  const toggleLoginForm = () => {
    setShowLoginForm(!showLoginForm);
    setShowRegisterForm(false);
  };

  const toggleRegisterForm = () => {
    setShowRegisterForm(!showRegisterForm);
    setShowLoginForm(false);
  };

  const toggleProfileForm = () => {
    setShowProfileForm(!showProfileForm);
  };

  const toggleOrders = () => {  // Přidána nová funkce
    setShowOrders(!showOrders);
  };

  const handleBookSelect = (isbn) => {
    setSelectedBookIsbn(isbn);
    setCurrentView('detail');
  };

  const handleBackToList = () => {
    setCurrentView('list');
    setSelectedBookIsbn(null);
  };

  const toggleShoppingCart = () => {
    setCurrentView('cart');
    setShowShoppingCart(true);
  };

  const handleBackFromCart = () => {
    setCurrentView('list');
    setShowShoppingCart(false);
  };

  // Loading a Error stavy
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

  // Render
  return (
    <div className="App">
      <Header 
        language={language}
        toggleLanguage={toggleLanguage}
        user={user}
        handleLogout={handleLogout}
        toggleLoginForm={toggleLoginForm}
        toggleRegisterForm={toggleRegisterForm}
        toggleProfileForm={toggleProfileForm}
        toggleShoppingCart={toggleShoppingCart}
        toggleOrders={toggleOrders}  // Přidán nový prop
        translations={translations}
        toggleAuditLog={toggleAuditLog}
      />
      
      {showLoginForm && (
        <LoginForm 
          onLogin={handleLogin} 
          translations={translations} 
          language={language} 
        />
      )}

      {showAuditLog && <AuditLog onClose={toggleAuditLog} />}

      
      {showRegisterForm && (
        <RegisterForm 
          onRegister={handleRegister} 
          translations={translations} 
          language={language} 
        />
      )}

      {showProfileForm && (
        <ProfileForm 
          onUpdate={handleProfileUpdate}
          onClose={() => setShowProfileForm(false)}
          translations={translations}
          language={language}
          userData={user}
        />
      )}

      {showOrders && (  // Přidáno zobrazení OrderList
        <OrderList
          translations={translations}
          language={language}
          onClose={() => setShowOrders(false)}
        />
      )}

      {currentView === 'list' && (
        <>
          <SearchForm 
            searchQueries={searchQueries}
            handleSearchChange={handleSearchChange}
            handleSearchSubmit={handleSearchSubmit}
            handleClearSearch={handleClearSearch}
            currentSearchQueries={currentSearchQueries}
            translations={translations}
            language={language}
            showFavorites={showFavorites}
            onToggleFavorites={handleToggleFavorites}
            user={user}
          />

          {books.length > 0 ? (
            <>
              <BookList 
                books={books}
                translations={translations}
                language={language}
                onBookSelect={handleBookSelect}
                user={user}
                showFavorites={showFavorites}
              />
              <Pagination 
                currentPage={currentPage}
                totalPages={totalPages}
                handlePageChange={handlePageChange}
                translations={translations}
                language={language}
              />
            </>
          ) : (
            <div className="no-results">
              {showFavorites 
                ? translations[language].noFavoriteBooks 
                : translations[language].noResults}
            </div>
          )}
        </>
      )}

      {currentView === 'detail' && (
        <BookDetail 
          isbn={selectedBookIsbn}
          translations={translations}
          language={language}
          onBackToList={handleBackToList}
          user={user}
          showFavorites={showFavorites}
          onToggleFavorites={handleToggleFavorites}
        />
      )}

      {currentView === 'cart' && (
        <ShoppingCart 
          language={language}
          translations={translations}
          user={user}
          onBackToList={handleBackFromCart}
        />
      )}
    </div>
  );
}

export default App;