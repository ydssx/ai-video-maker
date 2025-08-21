import api from '../utils/api';
import { message } from 'antd';

const authService = {
  // 用户登录
  async login(credentials) {
    console.log('开始登录，凭据:', credentials);
    try {
      console.log('发送登录请求到 /users/login');
      const response = await api.post('/users/login', {
        username: credentials.username,
        password: credentials.password,
      });
      console.log('登录响应:', response);
      
      // 保存token和用户信息到localStorage
      if (response && response.access_token) {
        localStorage.setItem('token', response.access_token);
        // 获取用户信息
        const user = await this.getCurrentUser();
        localStorage.setItem('user', JSON.stringify(user));
        return { user, token: response.access_token };
      }
      
      throw new Error('登录失败，请检查用户名或密码');
    } catch (error) {
      console.error('登录出错:', error);
      const errorMessage = error.response?.data?.detail || '登录失败，请稍后重试';
      console.error('错误信息:', errorMessage);
      message.error(errorMessage);
      throw error;
    }
  },

  // 用户注册
  async register(userData) {
    try {
      const response = await api.post('/users/register', {
        username: userData.username,
        email: userData.email,
        password: userData.password,
      });
      
      message.success('注册成功！请登录');
      return response;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || '注册失败，请稍后重试';
      message.error(Array.isArray(errorMsg) ? errorMsg.join('\n') : errorMsg);
      throw error;
    }
  },

  // 获取当前用户信息
  async getCurrentUser() {
    try {
      // 从本地存储获取用户ID
      const token = localStorage.getItem('token');
      if (!token) return null;
      
      // 简化版本：由于后端默认返回用户ID为1的用户
      const response = await api.get('/users/profile');
      return response;
    } catch (error) {
      // 如果token无效，清除本地存储的token和用户信息
      if (error.response && error.response.status === 401) {
        this.logout();
      }
      console.error('获取用户信息失败:', error);
      return null;
    }
  },

  // 刷新token - 简化版本
  async refreshToken() {
    // 简化版本：直接返回当前token
    return localStorage.getItem('token');
  },

  // 退出登录
  logout() {
    // 调用后端API退出登录（如果需要）
    // await api.post('/auth/logout');
    
    // 清除本地存储的认证信息
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    
    // 重定向到登录页
    window.location.href = '/login';
  },

  // 检查用户是否已登录
  isAuthenticated() {
    return !!localStorage.getItem('token');
  },

  // 获取认证头部
  getAuthHeader() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  },

  // 检查用户是否已登录
  isAuthenticated() {
    return !!localStorage.getItem('token');
  }
};

export default authService;
