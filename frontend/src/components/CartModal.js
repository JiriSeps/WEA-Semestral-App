import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Trash2 } from 'lucide-react';

const CartModal = ({ 
  isOpen, 
  onClose, 
  user, 
  language, 
  translations, 
  toggleCart 
}) => {
  const [cartItems, setCartItems] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const fetchCartItems = async () => {
    if (!user) return;
  
    setIsLoading(true);
    try {
      const response = await axios.get('http://localhost:8007/api/shoppingcart', {
        params: { page }
      });
      
      setCartItems(response.data.books);
      setTotalPages(response.data.total_pages);
    } catch (error) {
      console.error('Error fetching cart items:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const removeFromCart = async (isbn) => {
    try {
      await axios.post(`/api/shoppingcart/${isbn}`);
      fetchCartItems();
    } catch (error) {
      console.error('Error removing item from cart:', error);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchCartItems();
    }
  }, [isOpen, page]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg w-[600px] max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-bold">
            {translations[language].shoppingCart}
          </h2>
          <button 
            onClick={onClose} 
            className="text-gray-500 hover:text-gray-700"
          >
            <X size={24} />
          </button>
        </div>

        {/* Cart Items */}
        <div className="overflow-y-auto flex-grow p-4">
          {isLoading ? (
            <p>{translations[language].loading}</p>
          ) : cartItems.length === 0 ? (
            <p>{translations[language].emptyCart}</p>
          ) : (
            cartItems.map(book => (
              <div 
                key={book.ISBN13} 
                className="flex items-center border-b py-2"
              >
                <img 
                  src={book.Cover_Image} 
                  alt={book.Title} 
                  className="w-16 h-24 object-cover mr-4"
                />
                <div className="flex-grow">
                  <h3 className="font-bold">{book.Title}</h3>
                  <p className="text-gray-600">{book.Author}</p>
                  <p className="font-semibold">{book.Price} CZK</p>
                </div>
                <button 
                  onClick={() => removeFromCart(book.ISBN13)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            ))
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center p-4">
            {[...Array(totalPages)].map((_, index) => (
              <button
                key={index}
                onClick={() => setPage(index + 1)}
                className={`mx-1 px-3 py-1 rounded ${
                  page === index + 1 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
        )}

        {/* Footer */}
        <div className="p-4 border-t flex justify-between items-center">
          <span className="font-bold">
            {translations[language].total}: {' '}
            {cartItems.reduce((total, book) => total + book.Price, 0).toFixed(2)} CZK
          </span>
          <button 
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            onClick={() => {/* Implement checkout logic */}}
          >
            {translations[language].checkout}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CartModal;