import React, { useState } from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';
import { useAppContext } from '../contexts/AppContext';

const LoginPage = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { actions } = useAppContext();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await login(values);
      const { access_token, user } = response.data;
      
      localStorage.setItem('token', access_token);
      actions.setUser(user);
      actions.setIsAuthenticated(true);
      
      message.success('登录成功！');
      navigate('/');
    } catch (error) {
      message.error(error.response?.data?.detail || '登录失败，请检查您的凭据。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Card title="登录" style={{ width: 400 }}>
        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入您的用户名!' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入您的密码!' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} style={{ width: '100%' }}>
              登录
            </Button>
          </Form.Item>
          <div style={{ textAlign: 'center' }}>
            还没有账户？ <a href="/register">立即注册</a>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;
