import React, { useState, useEffect } from 'react';
import axios from 'axios';

function RegisterForm({ onRegister, translations, language }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  // Efekt pro aktualizaci chybové hlášky při změně jazyka
  useEffect(() => {
    if (error) {
      setError(translations[language].registerError);
    }
  }, [language, translations]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8007/api/register', { username, password, name });
      onRegister();
    } catch (error) {
      setError(translations[language].registerError);
    }
  };

  return (
    <div className="auth-form">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder={translations[language].username}
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={translations[language].password}
          required
        />
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder={translations[language].name}
          required
        />
        <button type="submit">{translations[language].register}</button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}

export default RegisterForm;