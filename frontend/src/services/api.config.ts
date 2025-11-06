/**
 * API Configuration
 * 
 * Base configuration for API calls using environment variables
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const API_ENDPOINTS = {
  BASE_URL: API_BASE_URL,
  API_URL: API_URL,
  AUTH: {
    TOKEN: `${API_URL}/token/`,
    TOKEN_REFRESH: `${API_URL}/token/refresh/`,
    TOKEN_VERIFY: `${API_URL}/token/verify/`,
  },
};

export default API_ENDPOINTS;
