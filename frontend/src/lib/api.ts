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
    // If we get a network error (backend offline), intercept and return demo data for smooth UX
    if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      console.warn("Backend offline, returning mock data for demo UX.", error.config.url);
      const url = error.config.url || '';
      
      let mockData = null;
      if (url.includes('/challenges/data/heatmap')) {
        mockData = [
          { latitude: 23.3441, longitude: 85.3096, count: 12 },
          { latitude: 23.7957, longitude: 86.4304, count: 8 },
          { latitude: 22.8046, longitude: 86.2029, count: 5 }
        ];
      } else if (url.includes('/institutions/')) {
        mockData = {
          data: [
            { id: "1", name: "IIT (ISM) Dhanbad", district: "Dhanbad", state: "Jharkhand", student_count: 5000, is_verified: true, domains: ["Technology", "Energy"] },
            { id: "2", name: "NIT Jamshedpur", district: "East Singhbhum", state: "Jharkhand", student_count: 3500, is_verified: true, domains: ["Engineering"] }
          ]
        };
      } else if (url.includes('/challenges/')) {
        mockData = {
          data: [
            { id: "101", title: "Frequent Flooding in Sector 4", domain: "Urban Development", district: "Ranchi", status: "SUBMITTED", severity: "HIGH", created_at: new Date().toISOString(), narrative: "The drainage system overflows after 2 hours of heavy rain." },
            { id: "102", title: "Smart Irrigation for Rural Areas", domain: "Agriculture", district: "Dhanbad", status: "MATCHED", severity: "MEDIUM", created_at: new Date().toISOString(), narrative: "Need an automated system for farmers." }
          ],
          total: 2
        };
      } else if (url.includes('/health')) {
        mockData = { status: "healthy", version: "1.0.0 (Demo Mode)" };
      }
      
      if (mockData !== null) {
        return Promise.resolve({ data: mockData, status: 200, statusText: 'OK', headers: {}, config: error.config });
      }
    }

    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');
      }
    }
    return Promise.reject(error);
  }
);
