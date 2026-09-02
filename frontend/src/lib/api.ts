import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const classifierApi = axios.create({
  baseURL: process.env.NEXT_PUBLIC_CLASSIFIER_URL || 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach JWT token if available
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Setup response interceptor to handle 401s (refresh token logic can go here)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If we get a 401, we could try to refresh the token, but for now we just clear and redirect
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');
        // window.location.href = '/login'; // Optional: auto-redirect
      }
    }
    return Promise.reject(error);
  }
);
