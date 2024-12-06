// src/config.js
const config = {
    development: {
      apiUrl: 'http://localhost:8007'
    },
    production: {
      apiUrl: 'http://wea.nti.tul.cz:8007'
    }
  };
  
  const environment = window.location.hostname === 'wea.nti.tul.cz' ? 'production' : 'development';
  export const API_BASE_URL = config[environment].apiUrl;