import React from 'react';

export const Header = ({ language, toggleLanguage, user, handleLogout, toggleLoginForm, toggleRegisterForm, translations }) => (
  <div className="header">
    <button onClick={toggleLanguage} className="language-toggle">
      {language === 'cs' ? 'EN' : 'CS'}
    </button>
    <h1>{translations[language].title}</h1>
    {user ? (
      <div className="auth-buttons logged-in">
        <span className="welcome-message">{translations[language].welcomeMessage}{user.name}</span>
        <button onClick={handleLogout} className="logout-button">{translations[language].logout}</button>
      </div>
    ) : (
      <div className="auth-buttons">
        <button onClick={toggleLoginForm} className="auth-button">{translations[language].login}</button>
        <button onClick={toggleRegisterForm} className="auth-button">{translations[language].register}</button>
      </div>
    )}
  </div>
);