import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Trash2 } from 'lucide-react';
import OrderForm from './OrderForm';

const ShoppingCart = ({ 
  language, 
  translations, 
  user,
  onBackToList 
}) => {
  const [cartItems, setCartItems] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [isCartLoading, setIsCartLoading] = useState(false);
  const [showOrderForm, setShowOrderForm] = useState(false);

  const fetchCartItems = async () => {
    if (!user) return;
  
    setIsLoading(true);
    try {
      const response = await axios.get('http://localhost:8007/api/shoppingcart', {
        params: { page },
        headers: {
          'Accept': 'application/json'
        }
      });
  
      setCartItems(response.data.books);
      setTotalPages(response.data.total_pages);
      
      setStatusMessage({
        type: 'success',
        text: response.data.message || translations[language].cartLoaded
      });
  
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || translations[language].cartError;
      setStatusMessage({
        type: 'error',
        text: errorMessage
      });
      console.error('Error fetching cart items:', error);
    } finally {
      setIsLoading(false);
      setTimeout(() => setStatusMessage(null), 3000);
    }
  };

  const removeFromCart = async (isbn) => {
    if (!isbn) {
      console.error('ISBN is required to remove item from cart');
      return;
    }

    setIsCartLoading(true);
    try {
      const response = await axios.post(
        `http://localhost:8007/api/shoppingcart/${isbn}`, 
        null,
        {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        }
      );;
      
      if (response.data.is_in_cart === false) {
        await fetchCartItems();
        
        setStatusMessage({
          type: 'success',
          text: response.data?.message || translations[language].removedFromCart
        });
      }
  
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || translations[language].removeError;
      setStatusMessage({
        type: 'error',
        text: errorMessage
      });
      console.error('Error removing item from cart:', error);
    } finally {
      setIsCartLoading(false);
      setTimeout(() => setStatusMessage(null), 3000);
    }
  };

  const handleCheckout = () => {
    setShowOrderForm(true);
  };

  const handleOrderSubmit = async (orderData) => {
    try {
      setStatusMessage({
        type: 'success',
        text: translations[language].orderSuccess
      });
      
      await fetchCartItems();
      setShowOrderForm(false);
    } catch (error) {
      setStatusMessage({
        type: 'error',
        text: translations[language].orderError
      });
    }
  };

  const handleOrderClose = () => {
    setShowOrderForm(false);
  };

  useEffect(() => {
    let mounted = true;

    if (mounted) {
      fetchCartItems();
    }

    return () => {
      mounted = false;
    };
  }, [page, user]);

  if (isLoading) {
    return (
      <div className="cart-loading-container">
        <div className="cart-loading-text">{translations[language].loading}</div>
      </div>
    );
  }

  return (
    <div className="cart-card">
      <div className="cart-page-container">
        {/* Back Button */}
        <button
          onClick={onBackToList}
          className="cart-back-button"
        >
          ← {translations[language].back}
        </button>

        <div className="cart-content-wrapper">
          {/* Status Message */}
          {statusMessage && (
            <div className={`cart-status-message ${
              statusMessage.type === 'success' 
                ? 'bg-green-100 text-green-700' 
                : 'bg-red-100 text-red-700'
            }`}>
              {statusMessage.text}
            </div>
          )}

          {/* Main Content */}
          <div className="cart-main-panel">
            {/* Header */}
            <div className="cart-header">
              <h1 className="cart-title">
                {translations[language].shoppingCart}
              </h1>
            </div>

            {/* Cart Items */}
            <div className="cart-items-container">
              {cartItems.length === 0 ? (
                <div className="cart-empty-state">
                  <p className="cart-empty-message">
                    {translations[language].emptyCart}
                  </p>
                </div>
              ) : (
                <div className="cart-items-list">
                  {cartItems.map(book => (
                    <div 
                      key={book.ISBN13} 
                      className="cart-item"
                    >
                      <img 
                        src={book.Cover_Image} 
                        alt={book.Title} 
                        className="cart-item-image"
                        onError={(e) => {
                          e.target.src = '/placeholder-book.png';
                          e.target.onerror = null;
                        }}
                      />
                      <div className="cart-item-details">
                        <h3 className="cart-item-title">{book.Title}</h3>
                        <p className="cart-item-author">{book.Author}</p>
                        <p className="cart-item-isbn">ISBN: {book.ISBN13}</p>
                        <p className="cart-item-price">
                          {book.Price.toFixed(2)} CZK
                        </p>
                      </div>
                      <button 
                        onClick={() => removeFromCart(book.ISBN13)}
                        className="cart-item-remove-button"
                        disabled={isCartLoading}
                        aria-label={`Remove ${book.Title} from cart`}
                      >
                        <Trash2 size={24} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="cart-pagination">
                {[...Array(totalPages)].map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setPage(index + 1)}
                    className={`cart-page-button ${
                      page === index + 1 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                    aria-label={`Page ${index + 1}`}
                    aria-current={page === index + 1 ? 'page' : undefined}
                  >
                    {index + 1}
                  </button>
                ))}
              </div>
            )}

            {/* Footer with Total and Checkout */}
            {cartItems.length > 0 && (
              <div className="cart-footer">
                <div className="cart-footer-content">
                  <div className="cart-total">
                    {translations[language].total}: {' '}
                    {cartItems.reduce((total, book) => total + book.Price, 0).toFixed(2)} CZK
                  </div>
                  <button 
                    className="cart-checkout-button"
                    onClick={handleCheckout}
                  >
                    {translations[language].checkout}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Order Form Modal */}
        {showOrderForm && (
          <OrderForm
            onSubmit={handleOrderSubmit}
            onClose={handleOrderClose}
            translations={translations}
            language={language}
            userData={user}
            cartItems={cartItems}
          />
        )}
      </div>
    </div>
  );
};

export default ShoppingCart;