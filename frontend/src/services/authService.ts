import axios from 'axios';
import api from '../utils/api';

export type LoginCredentials = { username: string; password: string };
export type RegisterData = { username: string; email: string; password: string };
export type AuthUser = Record<string, unknown> | null;
export type LoginResponseBody = { access_token?: string };

const authService = {
  async login(credentials: LoginCredentials) {
    console.log('开始登录，凭据:', credentials);
    try {
      console.log('发送登录请求到 /users/login');
      const form = new URLSearchParams();
      form.append('username', credentials.username);
      form.append('password', credentials.password);
      form.append('grant_type', 'password');
      form.append('scope', '');
      const response = (await api.post<LoginResponseBody>('/users/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })) as LoginResponseBody;
      console.log('登录响应:', response);

      if (response && response.access_token) {
        localStorage.setItem('token', response.access_token);
        const user = await this.getCurrentUser();
        localStorage.setItem('user', JSON.stringify(user));
        return { user, token: response.access_token };
      }

      throw new Error('登录失败，请检查用户名或密码');
    } catch (error) {
      console.error('登录出错:', error);
      throw error;
    }
  },

  async register(userData: RegisterData) {
    try {
      const response = await api.post('/users/register', {
        username: userData.username,
        email: userData.email,
        password: userData.password,
      });

      return response;
    } catch (error) {
      throw error;
    }
  },

  async getCurrentUser(): Promise<AuthUser> {
    try {
      const token = localStorage.getItem('token');
      if (!token) return null;

      const response = await api.get<AuthUser>('/users/me');
      return response;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        this.logout();
      }
      console.error('获取用户信息失败:', error);
      return null;
    }
  },

  async refreshToken() {
    return localStorage.getItem('token');
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');

    window.location.href = '/login';
  },

  isAuthenticated() {
    return !!localStorage.getItem('token');
  },

  getAuthHeader() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  },
};

export default authService;
