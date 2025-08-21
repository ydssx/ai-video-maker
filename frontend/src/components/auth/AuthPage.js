import React, { useState, useEffect } from 'react';
import { Tabs, Form, Input, Button, Checkbox, Divider, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, GoogleOutlined, GithubOutlined } from '@ant-design/icons';
import { t } from '../../utils/i18n';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './AuthPage.css';

const { TabPane } = Tabs;

const AuthPage = ({ initialTab = 'login' }) => {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { login, register } = useAuth();
  
  // 处理重定向
  const from = location.state?.from?.pathname || '/';
  const redirect = searchParams.get('redirect') || from;

  const onFinish = async (values) => {
    setLoading(true);
    try {
      if (activeTab === 'login') {
        await login({
          username: values.username,
          password: values.password,
          remember: values.remember
        });
        message.success(t('auth.login.success', '登录成功！'));
        navigate(redirect, { replace: true });
      } else {
        await register({
          username: values.username,
          email: values.email,
          password: values.password
        });
        form.resetFields(['password', 'confirm']);
        setActiveTab('login');
      }
    } catch (error) {
      console.error('Authentication error:', error);
      // 错误信息已经在authService中处理
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (key) => {
    setActiveTab(key);
    form.resetFields();
  };

  const handleOAuthLogin = (provider) => {
    // 构造OAuth授权URL
    const oauthUrl = `${process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'}/auth/${provider.toLowerCase()}`;
    // 添加重定向URL
    const redirectUri = `${window.location.origin}${redirect}`;
    window.location.href = `${oauthUrl}?redirect_uri=${encodeURIComponent(redirectUri)}`;
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>{t('auth.title', 'AI 视频制作平台')}</h1>
          <p>{t('auth.subtitle', '使用AI技术轻松创建专业级视频内容')}</p>
        </div>
        
        <Tabs 
          activeKey={activeTab} 
          onChange={handleTabChange}
          centered
          className="auth-tabs"
        >
          <TabPane tab={t('auth.login', '登录')} key="login">
            <Form
              form={form}
              name="login"
              onFinish={onFinish}
              autoComplete="off"
              layout="vertical"
              className="auth-form"
            >
              <Form.Item
                name="username"
                rules={[{ required: true, message: t('auth.usernameOrEmail.required', '请输入用户名或邮箱') }]}
              >
                <Input 
                  prefix={<UserOutlined />} 
                  placeholder={t('auth.usernameOrEmail.placeholder', '用户名或邮箱')} 
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="password"
                rules={[{ required: true, message: t('auth.password.required', '请输入密码') }]}
              >
                <Input.Password 
                  prefix={<LockOutlined />} 
                  placeholder={t('auth.password.placeholder', '密码')} 
                  size="large"
                />
              </Form.Item>

              <div className="form-extra">
                <Form.Item name="remember" valuePropName="checked" noStyle>
                  <Checkbox>{t('auth.remember', '记住我')}</Checkbox>
                </Form.Item>
                <a className="forgot-password" href="/forgot-password">
                  {t('auth.forgot', '忘记密码？')}
                </a>
              </div>

              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  size="large"
                  block
                >
                  {t('auth.login', '登录')}
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane tab={t('auth.register', '注册')} key="register">
            <Form
              form={form}
              name="register"
              onFinish={onFinish}
              autoComplete="off"
              layout="vertical"
              className="auth-form"
              scrollToFirstError
            >
              <Form.Item
                name="username"
                rules={[
                  { required: true, message: t('auth.username.required', '请输入用户名') },
                  { min: 4, message: t('auth.username.min', '用户名至少4个字符') },
                  { max: 20, message: t('auth.username.max', '用户名不能超过20个字符') }
                ]}
              >
                <Input 
                  prefix={<UserOutlined />} 
                  placeholder={t('auth.username.placeholder', '用户名')} 
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="email"
                rules={[
                  { type: 'email', message: t('auth.email.invalid', '请输入有效的邮箱地址') },
                  { required: true, message: t('auth.email.required', '请输入邮箱') }
                ]}
              >
                <Input 
                  prefix={<UserOutlined />} 
                  placeholder={t('auth.email.placeholder', '邮箱')} 
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="password"
                rules={[
                  { required: true, message: t('auth.password.required', '请输入密码') },
                  { min: 8, message: t('auth.password.min', '密码至少8个字符') },
                  {
                    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
                    message: t('auth.password.pattern', '密码必须包含大小写字母和数字'),
                  },
                ]}
                hasFeedback
              >
                <Input.Password 
                  prefix={<LockOutlined />} 
                  placeholder={t('auth.password.set', '设置密码')} 
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="confirm"
                dependencies={['password']}
                hasFeedback
                rules={[
                  {
                    required: true,
                    message: t('auth.confirm.required', '请确认密码'),
                  },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('password') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error(t('auth.confirm.mismatch', '两次输入的密码不匹配')));
                    },
                  }),
                ]}
              >
                <Input.Password 
                  prefix={<LockOutlined />} 
                  placeholder={t('auth.confirm.placeholder', '确认密码')} 
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="agreement"
                valuePropName="checked"
                rules={[
                  {
                    validator: (_, value) =>
                      value ? Promise.resolve() : Promise.reject(new Error(t('auth.agreement.required', '请阅读并同意用户协议'))),
                  },
                ]}
              >
                <Checkbox>
                  {t('auth.agreement.prefix', '我已阅读并同意')} <a href="/terms">{t('auth.terms', '用户协议')}</a> {t('auth.and', '和')} <a href="/privacy">{t('auth.privacy', '隐私政策')}</a>
                </Checkbox>
              </Form.Item>

              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  size="large"
                  block
                >
                  {t('auth.register', '注册')}
                </Button>
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>

        <Divider>{t('auth.or', '或')}</Divider>

        <div className="social-login">
          <Button 
            icon={<GoogleOutlined />} 
            className="social-btn google"
            onClick={() => handleOAuthLogin('Google')}
          >
            {t('auth.login.google', '使用 Google 登录')}
          </Button>
          <Button 
            icon={<GithubOutlined />} 
            className="social-btn github"
            onClick={() => handleOAuthLogin('GitHub')}
          >
            {t('auth.login.github', '使用 GitHub 登录')}
          </Button>
        </div>
      </div>
      
      <div className="auth-footer">
        {activeTab === 'login' ? (
          <span>{t('auth.footer.noAccount', '还没有账号？')}<a onClick={() => setActiveTab('register')}>{t('auth.footer.registerNow', '立即注册')}</a></span>
        ) : (
          <span>{t('auth.footer.hasAccount', '已有账号？')}<a onClick={() => setActiveTab('login')}>{t('auth.footer.loginNow', '立即登录')}</a></span>
        )}
        {activeTab === 'login' && (
          <div style={{ marginTop: 8 }}>
            <a href="/forgot-password">{t('auth.forgot', '忘记密码？')}</a>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuthPage;
