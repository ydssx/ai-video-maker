import axios, { type AxiosRequestConfig } from 'axios';
import { message } from 'antd';

export interface ApiClient {
  get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>;
  head<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>;
  delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>;
  post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>;
  put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>;
  patch<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>;
  request<T = unknown>(config: AxiosRequestConfig): Promise<T>;
}

// 创建 axios 实例；响应拦截器返回 data，故与默认 Axios 类型不同
const rawApi = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

rawApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

const shouldRetry = (error: { config?: AxiosRequestConfig & { _retryCount?: number }; response?: { status?: number } }) => {
  const config = error.config || {};
  const method = (config.method || 'get').toLowerCase();
  const isIdempotent = method === 'get' || method === 'head';
  const status = error.response?.status;
  const isNetwork = !error.response;
  const is5xx = status != null && status >= 500 && status < 600;
  return isIdempotent && (isNetwork || is5xx);
};

rawApi.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const config = (error.config || {}) as AxiosRequestConfig & { _retryCount?: number };
    config._retryCount = config._retryCount || 0;
    const maxRetries = 2;
    if (shouldRetry(error) && config._retryCount < maxRetries) {
      config._retryCount += 1;
      const backoff = 500 * Math.pow(2, config._retryCount - 1);
      await new Promise((r) => setTimeout(r, backoff));
      return rawApi(config);
    }

    const { response } = error;
    let errorMessage = '请求失败，请稍后重试';
    const urlStr = (error.config?.url || '').toString();
    const isAuthRequest = urlStr.includes('/users/login') || urlStr.includes('/users/register');

    if (response) {
      switch (response.status) {
        case 400:
          errorMessage = response.data?.detail || response.data?.message || '请求参数错误';
          break;
        case 401:
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          const currentPath = window.location.pathname;
          const isAuthPage = currentPath === '/login' || currentPath === '/register';
          if (!isAuthPage && !isAuthRequest) {
            window.location.href = '/login';
          }
          errorMessage = '登录已过期，请重新登录';
          break;
        case 403:
          errorMessage = '没有权限执行此操作';
          break;
        case 404:
          errorMessage = '请求的资源不存在';
          break;
        case 500:
          errorMessage = '服务器内部错误';
          break;
        default:
          errorMessage = response.data?.detail || response.data?.message || `请求失败: ${response.status}`;
      }
    } else if (error.message?.includes('timeout')) {
      errorMessage = '请求超时，请检查网络连接';
    } else if (error.message === 'Network Error') {
      errorMessage = '网络错误，请检查网络连接';
    }

    if (!isAuthRequest) {
      message.error(errorMessage);
    }
    return Promise.reject(error);
  }
);

const api = rawApi as unknown as ApiClient;

export default api;
