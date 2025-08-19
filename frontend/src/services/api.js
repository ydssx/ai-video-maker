import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the token in headers
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const login = (credentials) => {
  return apiClient.post('/users/login', credentials);
};

export const register = (userData) => {
  return apiClient.post('/users/register', userData);
};

export const getUserProfile = () => {
  return apiClient.get('/users/me');
};

export default apiClient;
