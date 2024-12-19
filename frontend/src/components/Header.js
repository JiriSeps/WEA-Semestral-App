import React from 'react';
import { ShoppingCart, Package } from 'lucide-react';

export const Header = ({ 
  language, 
  toggleLanguage, 
  user, 
  handleLogout, 
  toggleLoginForm, 
  toggleRegisterForm, 
  toggleProfileForm,
  toggleShoppingCart,
  toggleOrders, // přidáno
  toggleAuditLog,
  translations 
}) => (
  <div className="header flex items-center justify-between p-4">
    <div className="flex items-center space-x-4">
      <button onClick={toggleLanguage} className="language-toggle">
        {language === 'cs' ? 'EN' : 'CS'}
      </button>
      <h1>{translations[language].title}</h1>
    </div>
    
    <div className="flex items-center space-x-4">
      {user ? (
        <div className="auth-buttons logged-in flex items-center space-x-2">
          <span className="welcome-message">{translations[language].welcomeMessage}{user.name}</span>
          <button onClick={toggleProfileForm} className="profile-button">
            {translations[language].editProfile}
          </button>
          <button onClick={toggleOrders} className="orders-button">
            <Package size={24} />
          </button>
          <button 
            onClick={toggleShoppingCart}
            className="cart-button"
          >
            <ShoppingCart size={24} />
          </button>
          <button onClick={handleLogout} className="logout-button">
            {translations[language].logout}
          </button>

          {/* Audit Log Button for Admin */}
          {user?.role === 'ADMIN' && (
            <button onClick={toggleAuditLog} className="audit-log-button">
              {translations[language].auditLog}
            </button>
          )}
        </div>
      ) : (
        <div className="auth-buttons space-x-2">
          <button onClick={toggleLoginForm} className="auth-button">{translations[language].login}</button>
          <button onClick={toggleRegisterForm} className="auth-button">{translations[language].register}</button>
        </div>
      )}
    </div>
  </div>
);
