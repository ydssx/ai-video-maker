import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Layout, Button, Alert, Drawer, Space, Badge, Menu, Dropdown, Tooltip } from 'antd';
import {
  UserOutlined,
  SettingOutlined,
  QuestionCircleOutlined,
  FolderOutlined,
  DashboardOutlined,
  ArrowLeftOutlined,
  LogoutOutlined,
  MoreOutlined,
  PlayCircleOutlined,
  SettingOutlined as ConfigOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import { AppProvider, useAppContext } from './contexts/AppContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ScriptGenerator from './components/ScriptGenerator';
import OptimizedScriptGenerator from './components/OptimizedScriptGenerator';
import VideoPreview from './components/VideoPreview';
import StandaloneAssetManager from './components/StandaloneAssetManager';
import UserDashboard from './components/UserDashboard';
import StepNavigation from './components/StepNavigation';
import { FullScreenLoader } from './components/LoadingIndicator';
import PerformancePage from './components/performance/PerformancePage';
import AuthPage from './components/auth/AuthPage';
import PrivateRoute from './components/auth/PrivateRoute';
import './App.css';
import { t } from './utils/i18n';

const { Header, Content, Footer } = Layout;

// 主应用内容组件
const AppContent = () => {
  const { state, actions } = useAppContext();
  const { app, project } = state;
  const { logout } = useAuth();
  const location = useLocation();
  const [showUserDashboard, setShowUserDashboard] = useState(false);
  const [showAssetManager, setShowAssetManager] = useState(false);
  const [showPerformance, setShowPerformance] = useState(false);
  
  // 如果当前路径是登录或注册页面，则重定向到首页
  if (location.pathname === '/login' || location.pathname === '/register') {
    return <Navigate to="/" replace />;
  }

  const handleScriptGenerated = (generatedScript) => {
    actions.setScript(generatedScript);
    actions.setCurrentStep(1);
    actions.addNotification('脚本生成成功！现在可以配置视频设置了', 'success');
  };

  const handleVideoCreated = (createdVideoId) => {
    actions.setVideoId(createdVideoId);
    actions.setCurrentStep(3);
    actions.addNotification('视频制作完成！可以下载了', 'success');
  };

  const handleStepChange = (step) => {
    actions.setCurrentStep(step);
  };

  // 获取当前步骤的主CTA按钮
  const getMainCTAButton = () => {
    if (app.currentStep === 0) {
      return null; // 脚本生成步骤不需要主CTA
    }
    
    if (app.currentStep === 1) {
      return (
        <Tooltip title="配置完成后开始制作视频">
          <Button 
            type="primary" 
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={() => actions.setCurrentStep(2)}
            disabled={!project.script}
            style={{ marginLeft: 16 }}
          >
            开始制作视频
          </Button>
        </Tooltip>
      );
    }
    
    if (app.currentStep === 2) {
      return (
        <Tooltip title="预览并确认视频效果">
          <Button 
            type="primary" 
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={() => actions.setCurrentStep(3)}
            style={{ marginLeft: 16 }}
          >
            前往导出
          </Button>
        </Tooltip>
      );
    }
    
    if (app.currentStep === 3) {
      return (
        <Tooltip title="下载制作完成的视频">
          <Button 
            type="primary" 
            size="large"
            icon={<DownloadOutlined />}
            style={{ marginLeft: 16 }}
          >
            下载视频
          </Button>
        </Tooltip>
      );
    }
    
    return null;
  };

  const renderMainContent = () => {
    if (showPerformance) {
      return (
        <PerformancePage onBack={() => setShowPerformance(false)} />
      );
    }

    return (
      <>
        {/* 步骤导航 - 始终固定在顶部 */}
        <StepNavigation 
          onStepChange={handleStepChange}
          showProgress={true}
          showQuickActions={true}
          compact={false}
        />

        {/* 主要内容区域 */}
        <div className="main-content">
          {!showAssetManager ? (
            <>
              {app.currentStep === 0 && (
                <div className="step-content">
                  <OptimizedScriptGenerator onScriptGenerated={handleScriptGenerated} />
                </div>
              )}

              {app.currentStep >= 1 && app.currentStep <= 3 && (
                <div className="step-content">
                  {app.currentStep === 1 && (
                    <Alert
                      message="配置视频"
                      description="现在可以配置视频模板、样式、音频等设置，完成后点击右上角的'开始制作视频'按钮。"
                      type="info"
                      showIcon
                      style={{ marginBottom: 16 }}
                      closable
                    />
                  )}
                  <VideoPreview
                    script={project.script}
                    onVideoCreated={handleVideoCreated}
                  />
                </div>
              )}
            </>
          ) : (
            <div className="asset-manager-content">
              <div style={{ marginBottom: 16, textAlign: 'right' }}>
                <Button onClick={() => setShowAssetManager(false)}>
                  返回制作
                </Button>
              </div>
              <StandaloneAssetManager />
            </div>
          )}
        </div>
      </>
    );
  };

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div className="header-content">
          <h1 style={{ color: 'white', margin: 0, cursor: 'pointer' }} onClick={() => setShowPerformance(false)}>
            {showPerformance ? (
              <>
                <ArrowLeftOutlined style={{ marginRight: 8 }} />
                🎬 AI 短视频制作平台
              </>
            ) : (
              '🎬 AI 短视频制作平台'
            )}
          </h1>
          <div className="header-actions">
            <Space>
              {/* 主CTA按钮 */}
              {getMainCTAButton()}
              
              {/* 资源管理 - 主要功能 */}
              <Badge dot={project.isDirty}>
                <Button
                  type="link"
                  style={{ color: 'white' }}
                  icon={<FolderOutlined />}
                  onClick={() => setShowAssetManager(true)}
                >
                  资源管理
                </Button>
              </Badge>
              
              {/* 更多功能下拉菜单 */}
              <Dropdown
                overlay={
                  <Menu
                    items={[
                      { key: 'performance', label: t('header.performance'), icon: <DashboardOutlined />, onClick: () => setShowPerformance(!showPerformance) },
                      { key: 'user', label: t('header.user'), icon: <UserOutlined />, onClick: () => setShowUserDashboard(true) },
                      { key: 'settings', label: t('header.settings'), icon: <SettingOutlined /> },
                      { key: 'help', label: t('header.help'), icon: <QuestionCircleOutlined /> },
                      { type: 'divider' },
                      { key: 'logout', label: t('header.logout'), icon: <LogoutOutlined />, onClick: logout }
                    ]}
                  />
                }
                placement="bottomRight"
              >
                <Button type="link" style={{ color: 'white' }} icon={<MoreOutlined />}>
                  更多
                </Button>
              </Dropdown>
            </Space>
          </div>
        </div>
      </Header>

      <Content className="app-content">
        <div className="content-container">
          {renderMainContent()}
        </div>
      </Content>

      <Footer className="app-footer">
        <div style={{ textAlign: 'center' }}>
          AI 短视频制作平台 2024 - 让创作更简单
          {project.isDirty && (
            <span style={{ marginLeft: 16, color: '#faad14' }}>
            </span>
          )}
        </div>
      </Footer>

      {/* 用户中心抽屉 */}
      <Drawer
        title="👤 用户中心"
        placement="right"
        width={480}
        onClose={() => setShowUserDashboard(false)}
        open={showUserDashboard}
        bodyStyle={{ padding: '16px' }}
      >
        <UserDashboard />
      </Drawer>

      {/* 全屏加载器 */}
      <FullScreenLoader
        visible={app.loading}
        title="处理中..."
        description="请稍候，正在处理您的请求"
        showProgress={false}
      />
    </Layout>
  );
};

// 主应用组件
function App() {
  return (
    <Router>
      <AppProvider>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<AuthPage />} />
            <Route path="/register" element={<AuthPage initialTab="register" />} />
            <Route
              path="/*"
              element={
                <PrivateRoute>
                  <AppContent />
                </PrivateRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </AppProvider>
    </Router>
  );
}

export default App;