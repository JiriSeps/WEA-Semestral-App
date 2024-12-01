import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ProfileForm({ onUpdate, translations, language, onClose, userData }) {
  const [formData, setFormData] = useState({
    personal_street: '',
    personal_city: '',
    personal_postal_code: '',
    personal_country: '',
    billing_street: '',
    billing_city: '',
    billing_postal_code: '',
    billing_country: '',
    gdpr_consent: false,
    gender: '',
    age: '',
    favorite_genres: [],
    referral_source: ''
  });

  const [error, setError] = useState('');
  const [sameAsPersonal, setSameAsPersonal] = useState(false);
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isGenresOpen, setIsGenresOpen] = useState(false);

  // Načtení žánrů
  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const response = await axios.get('http://localhost:8007/api/genres');
        setGenres(response.data.genres);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching genres:", error);
        setLoading(false);
      }
    };

    fetchGenres();
  }, []);

  // Načtení dat uživatele
  useEffect(() => {
    if (userData) {
      setFormData({
        personal_street: userData.personal_address?.street || '',
        personal_city: userData.personal_address?.city || '',
        personal_postal_code: userData.personal_address?.postal_code || '',
        personal_country: userData.personal_address?.country || '',
        billing_street: userData.billing_address?.street || '',
        billing_city: userData.billing_address?.city || '',
        billing_postal_code: userData.billing_address?.postal_code || '',
        billing_country: userData.billing_address?.country || '',
        gdpr_consent: userData.gdpr_consent || false,
        gender: userData.gender || '',
        age: userData.age || '',
        favorite_genres: userData.favorite_genres || [],
        referral_source: userData.referral_source || ''
      });

      // Kontrola, zda jsou adresy stejné
      const personalAddressFields = ['street', 'city', 'postal_code', 'country'];
      const addressesMatch = personalAddressFields.every(field =>
        userData.personal_address?.[field] === userData.billing_address?.[field]
      );
      setSameAsPersonal(addressesMatch);
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
    setSameAsPersonal(e.target.checked);
    if (e.target.checked) {
      setFormData(prev => ({
        ...prev,
        billing_street: prev.personal_street,
        billing_city: prev.personal_city,
        billing_postal_code: prev.personal_postal_code,
        billing_country: prev.personal_country
      }));
    }
  };

  const toggleGenres = () => {
    setIsGenresOpen(!isGenresOpen);
  };

  const handleGenreChange = (genre) => {
    setFormData(prev => ({
      ...prev,
      favorite_genres: prev.favorite_genres.includes(genre)
        ? prev.favorite_genres.filter(g => g !== genre)
        : [...prev.favorite_genres, genre]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put('http://localhost:8007/api/user/profile', formData);
      onUpdate(response.data.user);
      onClose();
    } catch (error) {
      setError(translations[language].updateError);
    }
  };

  return (
    <div className="profile-form-overlay">
      <div className="profile-form">
        <form onSubmit={handleSubmit}>
          <div className="form-header">
            <h2>{translations[language].editProfile}</h2>
            <button type="button" className="close-button" onClick={onClose}>×</button>
          </div>

          {/* Osobní adresa */}
          <div className="form-section">
            <h3>{translations[language].personalAddress}</h3>
            <input
              type="text"
              name="personal_street"
              value={formData.personal_street}
              onChange={handleChange}
              placeholder={translations[language].street}
              className="form-input"
            />
            <input
              type="text"
              name="personal_city"
              value={formData.personal_city}
              onChange={handleChange}
              placeholder={translations[language].city}
              className="form-input"
            />
            <input
              type="text"
              name="personal_postal_code"
              value={formData.personal_postal_code}
              onChange={handleChange}
              placeholder={translations[language].postalCode}
              className="form-input"
            />
            <input
              type="text"
              name="personal_country"
              value={formData.personal_country}
              onChange={handleChange}
              placeholder={translations[language].country}
              className="form-input"
            />
          </div>

          {/* Checkbox pro stejnou adresu */}
          <div className="same-address-checkbox">
            <label>
              <input
                type="checkbox"
                checked={sameAsPersonal}
                onChange={handleSameAddressChange}
              />
              <span>{translations[language].sameAsBilling}</span>
            </label>
          </div>

          {/* Fakturační adresa */}
          {!sameAsPersonal && (
            <div className="form-section">
              <h3>{translations[language].billingAddress}</h3>
              <input
                type="text"
                name="billing_street"
                value={formData.billing_street}
                onChange={handleChange}
                placeholder={translations[language].street}
                className="form-input"
              />
              <input
                type="text"
                name="billing_city"
                value={formData.billing_city}
                onChange={handleChange}
                placeholder={translations[language].city}
                className="form-input"
              />
              <input
                type="text"
                name="billing_postal_code"
                value={formData.billing_postal_code}
                onChange={handleChange}
                placeholder={translations[language].postalCode}
                className="form-input"
              />
              <input
                type="text"
                name="billing_country"
                value={formData.billing_country}
                onChange={handleChange}
                placeholder={translations[language].country}
                className="form-input"
              />
            </div>
          )}

          {/* Osobní údaje */}
          <div className="form-section">
            <h3>{translations[language].personalInfo}</h3>
            <div className="gender-select">
              <label>
                <input
                  type="radio"
                  name="gender"
                  value="male"
                  checked={formData.gender === 'male'}
                  onChange={handleChange}
                />
                <span>{translations[language].male}</span>
              </label>
              <label>
                <input
                  type="radio"
                  name="gender"
                  value="female"
                  checked={formData.gender === 'female'}
                  onChange={handleChange}
                />
                <span>{translations[language].female}</span>
              </label>
            </div>

            <label htmlFor="age">{translations[language].age}</label>
            <input
              id="age" 
              type="number"
              name="age"
              value={formData.age}
              onChange={handleChange}
              placeholder={translations[language].age}
              className="form-input"
              min="0"
              max="150"
            />
          </div>

          {/* Žánry */}
          <div className="form-section genres-section">
            <div className="genres-field">
              <label>{translations[language].favoriteGenres}</label>
              <button
                type="button"
                className="genres-dropdown-button"
                onClick={toggleGenres}
              >
                {translations[language].genres}
                ({formData.favorite_genres.length} {translations[language].selected})
                <span className={`arrow ${isGenresOpen ? 'up' : 'down'}`}>▼</span>
              </button>
              {isGenresOpen && !loading && (
                <div className="genres-dropdown">
                  {genres.map(genre => (
                    <label key={genre} className="genre-checkbox">
                      <input
                        type="checkbox"
                        checked={formData.favorite_genres.includes(genre)}
                        onChange={() => handleGenreChange(genre)}
                      />
                      <span>{genre}</span>
                    </label>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Reference */}
          <div className="form-section">
            <label>{translations[language].referralSource}</label>
            <select
              name="referral_source"
              value={formData.referral_source}
              onChange={handleChange}
              className="form-select"
            >
              <option value="">{translations[language].selectReferral}</option>
              <option value="google">Google</option>
              <option value="friend">{translations[language].friend}</option>
              <option value="social">{translations[language].social}</option>
              <option value="other">{translations[language].other}</option>
            </select>
          </div>

          {/* GDPR souhlas */}
          <div className="gdpr-consent">
            <label>
              <input
                type="checkbox"
                name="gdpr_consent"
                checked={formData.gdpr_consent}
                onChange={handleChange}
              />
              <span>{translations[language].gdprConsent}</span>
            </label>
          </div>

          {error && <div className="error">{error}</div>}

          {/* Tlačítka */}
          <div className="form-buttons">
            <button type="submit" className="save-button">
              {translations[language].save}
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

export default ProfileForm;