import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import { message } from 'antd';
import axios from 'axios';
import authService from '../services/authService';

export type AuthUser = Record<string, unknown> | null;

export type LoginPayload = { username: string; password: string; remember?: boolean };
export type RegisterPayload = { username: string; email: string; password: string };

export type AuthContextValue = {
  currentUser: AuthUser;
  isAuthenticated: boolean;
  loading: boolean;
  login: (userData: LoginPayload) => Promise<AuthUser>;
  register: (userData: RegisterPayload) => Promise<boolean>;
  logout: () => void;
  updateUser: (userData: Record<string, unknown>) => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [currentUser, setCurrentUser] = useState<AuthUser>(null);
  const [loading, setLoading] = useState(true);

  const fetchCurrentUser = useCallback(async () => {
    try {
      if (authService.isAuthenticated()) {
        const user = await authService.getCurrentUser();
        setCurrentUser(user);
        if (user) {
          localStorage.setItem('user', JSON.stringify(user));
        }
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

  const login = async (userData: LoginPayload) => {
    try {
      const response = await authService.login({
        username: userData.username,
        password: userData.password,
      });

      setCurrentUser(response.user);
      message.success('登录成功！');
      return response.user;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        message.error(
          error.response?.data?.detail ||
            error.response?.data?.message ||
            '登录失败，请检查用户名或密码'
        );
      } else {
        message.error('登录失败，请检查用户名或密码');
      }
      throw error;
    }
  };

  const register = async (userData: RegisterPayload) => {
    try {
      await authService.register({
        username: userData.username,
        email: userData.email,
        password: userData.password,
      });

      message.success('注册成功！请登录');
      return true;
    } catch (error) {
      let errorMessage = '注册失败';
      if (axios.isAxiosError(error)) {
        const errorDetail =
          error.response?.data?.detail || error.response?.data?.message || '注册失败';
        errorMessage = Array.isArray(errorDetail)
          ? errorDetail.map((e: { msg?: string }) => e.msg || String(e)).join('; ')
          : String(errorDetail);
      }
      message.error(errorMessage);
      throw error;
    }
  };

  const logout = useCallback(() => {
    authService.logout();
    setCurrentUser(null);
    message.success('已退出登录');
  }, []);

  const updateUser = (userData: Record<string, unknown>) => {
    const updatedUser = { ...(currentUser || {}), ...userData };
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
