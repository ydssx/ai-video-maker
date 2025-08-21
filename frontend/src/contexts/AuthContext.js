import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { message } from 'antd';
import authService from '../services/authService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 获取当前用户信息
  const fetchCurrentUser = useCallback(async () => {
    try {
      if (authService.isAuthenticated()) {
        const user = await authService.getCurrentUser();
        setCurrentUser(user);
        localStorage.setItem('user', JSON.stringify(user));
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  const login = async (userData) => {
    try {
      const response = await authService.login({
        username: userData.username,
        password: userData.password
      });
      
      // 更新用户状态
      setCurrentUser(response.user);
      message.success('登录成功！');
      return response.user;
    } catch (error) {
      message.error(error.response?.data?.message || '登录失败，请检查用户名或密码');
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      await authService.register({
        username: userData.username,
        email: userData.email,
        password: userData.password
      });
      
      message.success('注册成功！请登录');
      return true;
    } catch (error) {
      const errorMessage = error.response?.data?.message || '注册失败';
      message.error(Array.isArray(errorMessage) ? errorMessage.join('\n') : errorMessage);
      throw error;
    }
  };

  const logout = useCallback(() => {
    authService.logout();
    setCurrentUser(null);
    message.success('已退出登录');
  }, []);

  const updateUser = (userData) => {
    const updatedUser = { ...currentUser, ...userData };
    setCurrentUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        isAuthenticated: !!currentUser,
        loading,
        login,
        register,
        logout,
        updateUser,
      }}
    >
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
