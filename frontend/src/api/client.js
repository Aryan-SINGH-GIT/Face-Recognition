import axios from 'axios';

let rawBase = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
if (rawBase && !rawBase.startsWith('http://') && !rawBase.startsWith('https://')) {
  rawBase = `https://${rawBase}`;
}
const BASE_URL = rawBase;

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
});

// Attach JWT token to every request if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('jwt_token');
      localStorage.removeItem('admin_role');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;
