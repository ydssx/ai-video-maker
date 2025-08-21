import axios from 'axios';
import { message } from 'antd';

// 创建axios实例
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
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

// 简单重试策略（仅对 GET/HEAD 且网络错误或 5xx 生效）
const shouldRetry = (error) => {
  const config = error.config || {};
  const method = (config.method || 'get').toLowerCase();
  const isIdempotent = method === 'get' || method === 'head';
  const status = error.response?.status;
  const isNetwork = !error.response;
  const is5xx = status && status >= 500 && status < 600;
  return isIdempotent && (isNetwork || is5xx);
};

api.interceptors.response.use(
	(response) => {
		return response.data;
	},
	async (error) => {
		const config = error.config || {};
		config._retryCount = config._retryCount || 0;
		const maxRetries = 2;
		if (shouldRetry(error) && config._retryCount < maxRetries) {
			config._retryCount += 1;
			const backoff = 500 * Math.pow(2, config._retryCount - 1);
			await new Promise((r) => setTimeout(r, backoff));
			return api(config);
		}

		const { response } = error;
		let errorMessage = '请求失败，请稍后重试';
		
		if (response) {
			// 处理HTTP错误状态码
			switch (response.status) {
				case 400:
					errorMessage = response.data?.message || '请求参数错误';
					break;
				case 401:
					// 未授权，清除token并跳转到登录页
					localStorage.removeItem('token');
					localStorage.removeItem('user');
					window.location.href = '/login';
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
					errorMessage = response.data?.message || `请求失败: ${response.status}`;
			}
		} else if (error.message?.includes('timeout')) {
			errorMessage = '请求超时，请检查网络连接';
		} else if (error.message === 'Network Error') {
			errorMessage = '网络错误，请检查网络连接';
		}

		message.error(errorMessage);
		return Promise.reject(error);
	}
);

export default api;
