import React, { useState, useEffect } from 'react';
import axios from 'axios';

function OrderForm({ onSubmit, translations, language, onClose, userData, cartItems }) {
  const [formData, setFormData] = useState({
    email: '',
    shipping_street: '',
    shipping_city: '',
    shipping_postal_code: '',
    shipping_country: '',
    billing_street: '',
    billing_city: '',
    billing_postal_code: '',
    billing_country: '',
    payment_method: '',
    gdpr_consent: false
  });

  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [sameAsShipping, setSameAsShipping] = useState(false);
  const [paymentFee, setPaymentFee] = useState(0);

  // Výpočet ceny
  const subtotal = cartItems.reduce((sum, item) => sum + (item.Price * (item.quantity || 1)), 0);

  // Výpočet poplatku za platbu a celkové ceny
  useEffect(() => {
    let fee = 0;
    if (formData.payment_method === 'cash_on_delivery') {
      fee = 50;
    } else if (formData.payment_method === 'card_online') {
      fee = subtotal * 0.01;
    }
    setPaymentFee(fee);
  }, [formData.payment_method, subtotal]);

  // Načtení dat uživatele
  useEffect(() => {
    if (userData) {
      setFormData(prev => ({
        ...prev,
        email: userData.email || '',
        shipping_street: userData.personal_address?.street || '',
        shipping_city: userData.personal_address?.city || '',
        shipping_postal_code: userData.personal_address?.postal_code || '',
        shipping_country: userData.personal_address?.country || '',
        billing_street: userData.billing_address?.street || '',
        billing_city: userData.billing_address?.city || '',
        billing_postal_code: userData.billing_address?.postal_code || '',
        billing_country: userData.billing_address?.country || '',
        gdpr_consent: userData.gdpr_consent || false
      }));

      // Kontrola, zda jsou adresy stejné
      const addressFields = ['street', 'city', 'postal_code', 'country'];
      const addressesMatch = addressFields.every(field =>
        userData.personal_address?.[field] === userData.billing_address?.[field]
      );
      setSameAsShipping(addressesMatch);
    }
  }, [userData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSameAddressChange = (e) => {
    setSameAsShipping(e.target.checked);
    if (e.target.checked) {
      setFormData(prev => ({
        ...prev,
        billing_street: prev.shipping_street,
        billing_city: prev.shipping_city,
        billing_postal_code: prev.shipping_postal_code,
        billing_country: prev.shipping_country
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.gdpr_consent) {
      setError(translations[language].gdprRequired);
      return;
    }

    try {
      // Odeslání objednávky
      const orderData = {
        cart_items: cartItems.map(item => ({
          isbn: item.ISBN10 || item.ISBN13,
          quantity: 1,
          price: parseFloat(item.Price)
        })),
        email: formData.email,
        shipping_address: {
          street: formData.shipping_street,
          city: formData.shipping_city,
          postal_code: formData.shipping_postal_code,
          country: formData.shipping_country
        },
        billing_address: {
          street: sameAsShipping ? formData.shipping_street : formData.billing_street,
          city: sameAsShipping ? formData.shipping_city : formData.billing_city,
          postal_code: sameAsShipping ? formData.shipping_postal_code : formData.billing_postal_code,
          country: sameAsShipping ? formData.shipping_country : formData.billing_country
        },
        payment_method: formData.payment_method,
        payment_fee: parseFloat(paymentFee),
        total_price: parseFloat((subtotal + paymentFee).toFixed(2))
      };

      // Odeslání objednávky na server
      await axios.post('http://localhost:8007/api/orders', orderData, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        withCredentials: true
      });

      // Vyčištění košíku
      await axios.delete('http://localhost:8007/api/shoppingcart', {
        withCredentials: true
      });

      // Nastavení úspěšné zprávy
      setSuccessMessage(translations[language].orderSuccess);
      setError('');

      // Zavření formuláře po 2 sekundách
      setTimeout(() => {
        onSubmit(orderData);
      }, 2000);

    } catch (error) {
      console.error('Error creating order:', error);
      const errorMessage = error.response?.data?.error || translations[language].orderError;
      setError(errorMessage);
      setSuccessMessage('');
    }
  };

  return (
    <div className="order-form-overlay">
      <div className="order-form">
        <form onSubmit={handleSubmit}>
          <div className="form-header">
            <h2>{translations[language].createOrder}</h2>
            <button type="button" className="close-button" onClick={onClose}>×</button>
          </div>

          {/* Email sekce */}
          <div className="form-section">
            <h3>{translations[language].contactInfo}</h3>
            <label className="form-label">
              {translations[language].email}
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="form-input"
                required
              />
            </label>
          </div>

          {/* Doručovací adresa */}
          <div className="form-section">
            <h3>{translations[language].shippingAddress}</h3>
            <label className="form-label">
              {translations[language].street}
              <input
                type="text"
                name="shipping_street"
                value={formData.shipping_street}
                onChange={handleChange}
                className="form-input"
                required
              />
            </label>
            <label className="form-label">
              {translations[language].city}
              <input
                type="text"
                name="shipping_city"
                value={formData.shipping_city}
                onChange={handleChange}
                className="form-input"
                required
              />
            </label>
            <label className="form-label">
              {translations[language].postalCode}
              <input
                type="text"
                name="shipping_postal_code"
                value={formData.shipping_postal_code}
                onChange={handleChange}
                className="form-input"
                required
              />
            </label>
            <label className="form-label">
              {translations[language].country}
              <input
                type="text"
                name="shipping_country"
                value={formData.shipping_country}
                onChange={handleChange}
                className="form-input"
                required
              />
            </label>
          </div>

          {/* Checkbox pro stejnou adresu */}
          <div className="same-address-checkbox">
            <label>
              <input
                type="checkbox"
                checked={sameAsShipping}
                onChange={handleSameAddressChange}
              />
              <span>{translations[language].sameAsShipping}</span>
            </label>
          </div>

          {/* Fakturační adresa */}
          {!sameAsShipping && (
            <div className="form-section">
              <h3>{translations[language].billingAddress}</h3>
              <label className="form-label">
                {translations[language].street}
                <input
                  type="text"
                  name="billing_street"
                  value={formData.billing_street}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </label>
              <label className="form-label">
                {translations[language].city}
                <input
                  type="text"
                  name="billing_city"
                  value={formData.billing_city}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </label>
              <label className="form-label">
                {translations[language].postalCode}
                <input
                  type="text"
                  name="billing_postal_code"
                  value={formData.billing_postal_code}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </label>
              <label className="form-label">
                {translations[language].country}
                <input
                  type="text"
                  name="billing_country"
                  value={formData.billing_country}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </label>
            </div>
          )}

          {/* Platební metoda */}
          <div className="form-section">
            <h3>{translations[language].paymentMethod}</h3>
            <div className="payment-methods">
              <label>
                <input
                  type="radio"
                  name="payment_method"
                  value="cash_on_delivery"
                  checked={formData.payment_method === 'cash_on_delivery'}
                  onChange={handleChange}
                  required
                />
                <span>{translations[language].cashOnDelivery} (+50 Kč)</span>
              </label>
              <label>
                <input
                  type="radio"
                  name="payment_method"
                  value="bank_transfer"
                  checked={formData.payment_method === 'bank_transfer'}
                  onChange={handleChange}
                />
                <span>{translations[language].bankTransfer}</span>
              </label>
              <label>
                <input
                  type="radio"
                  name="payment_method"
                  value="card_online"
                  checked={formData.payment_method === 'card_online'}
                  onChange={handleChange}
                />
                <span>{translations[language].cardOnline} (+1%)</span>
              </label>
            </div>
          </div>

          {/* Cenový přehled */}
          <div className="price-summary">
            <div>{translations[language].subtotal}: {subtotal.toFixed(2)} Kč</div>
            <div>{translations[language].paymentFee}: {paymentFee.toFixed(2)} Kč</div>
            <div className="total-price">
              {translations[language].total}: {(subtotal + paymentFee).toFixed(2)} Kč
            </div>
          </div>

          {/* GDPR souhlas */}
          <div className="gdpr-consent">
            <label>
              <input
                type="checkbox"
                name="gdpr_consent"
                checked={formData.gdpr_consent}
                onChange={handleChange}
                required
              />
              <span>{translations[language].gdprConsent}</span>
            </label>
          </div>

          {error && <div className="error">{error}</div>}

          {/* Error a Success zprávy */}
          {error && <div className="error">{error}</div>}
          {successMessage && <div className="success-message">{successMessage}</div>}
          
          {/* Tlačítka */}
          <div className="form-buttons">
            <button type="submit" className="save-button">
              {translations[language].confirmOrder}
            </button>
            <button type="button" onClick={onClose} className="cancel-button">
              {translations[language].cancel}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}

export default OrderForm;