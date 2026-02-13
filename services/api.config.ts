
import axios from 'axios';

// Use environment variable for API URL, fallback to relative path for production
// In development with proxy, use '/api/v1'. For local backend, set VITE_API_URL='http://localhost:8000/api/v1'
const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('edunexia_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Tránh redirect loop: Chỉ chuyển hướng nếu lỗi 401 
    // Không redirect nếu đang ở trang login hoặc trang callback xác thực
    const isAuthPage = window.location.pathname.includes('/login') ||
      window.location.pathname.includes('/auth/callback');

    if (error.response?.status === 401 && !isAuthPage) {
      localStorage.removeItem('edunexia_token');
      localStorage.removeItem('edunexia_user');

      const details = error.response?.data?.detail || 'session_expired';
      window.location.href = `/login?error=unauthorized&details=${encodeURIComponent(details)}`;
    }
    return Promise.reject(error.response?.data || error);
  }
);

export const setAuthToken = (token: string) => {
  localStorage.setItem('edunexia_token', token);
};

export const clearAuthToken = () => {
  localStorage.removeItem('edunexia_token');
};
