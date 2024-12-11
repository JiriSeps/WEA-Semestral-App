import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const OrderList = ({ translations, language, onClose }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/orders`);
        setOrders(response.data.orders);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching orders:", error);
        setError(translations[language].loadError);
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="orders-overlay">
        <div className="orders-container">
          <div className="loading">{translations[language].loading}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="orders-overlay">
      <div className="orders-container">
        <div className="orders-header">
          <h2>{translations[language].myOrders}</h2>
          <button type="button" className="close-button" onClick={onClose}>×</button>
        </div>

        {error && <div className="error">{error}</div>}

        <div className="orders-list">
          {orders.length === 0 ? (
            <div className="no-orders">{translations[language].noOrders}</div>
          ) : (
            orders.map(order => (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <div className="order-id">
                    {translations[language].orderNumber}: {order.id}
                  </div>
                  <div className="order-date">
                    {translations[language].ordered}: {formatDate(order.created_at)}
                  </div>
                </div>

                <div className="order-status">
                  {translations[language].status}: {order.status}
                </div>

                <div className="order-items">
                  {order.items.map(item => (
                    <div key={`${order.id}-${item.book_isbn10}`} className="order-item">
                      <div className="item-title">{item.title}</div>
                      <div className="item-details">
                        {translations[language].quantity}: {item.quantity} × {item.price_per_item} Kč
                      </div>
                    </div>
                  ))}
                </div>

                <div className="order-summary">
                  <div className="order-address">
                    <h4>{translations[language].shippingAddress}</h4>
                    <div>{order.shipping_address.street}</div>
                    <div>{order.shipping_address.postal_code} {order.shipping_address.city}</div>
                    <div>{order.shipping_address.country}</div>
                  </div>

                  <div className="order-totals">
                    <div className="payment-method">
                      {translations[language].paymentMethod}: {order.payment_method}
                    </div>
                    {order.payment_fee > 0 && (
                      <div className="payment-fee">
                        {translations[language].paymentFee}: {order.payment_fee} Kč
                      </div>
                    )}
                    <div className="total-price">
                      {translations[language].totalPrice}: {order.total_price} Kč
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default OrderList;