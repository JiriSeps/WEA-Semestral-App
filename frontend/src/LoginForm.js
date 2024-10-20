import React, { useState, useEffect } from 'react';
import axios from 'axios';

function LoginForm({ onLogin, translations, language }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (error) {
      setError(translations[language].loginError);
    }
  }, [language, translations]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8007/api/login', { username, password });
      onLogin(response.data.user);
    } catch (error) {
      setError(translations[language].loginError);
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
        <button type="submit">{translations[language].login}</button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}

export default LoginForm;