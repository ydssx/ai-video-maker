import React, { useMemo, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import {
  Layout,
  Button,
  Drawer,
  Space,
  Badge,
  Menu,
  Dropdown,
  Tooltip,
  Grid,
  Segmented,
  Alert,
} from 'antd';
import {
  UserOutlined,
  SettingOutlined,
  QuestionCircleOutlined,
  FolderOutlined,
  DashboardOutlined,
  LogoutOutlined,
  MoreOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  VideoCameraOutlined,
  AppstoreOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { AppProvider, useAppContext } from './contexts/AppContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import OptimizedScriptGenerator from './components/OptimizedScriptGenerator';
import VideoPreview from './components/VideoPreview';
import StandaloneAssetManager from './components/StandaloneAssetManager';
import UserDashboard from './components/UserDashboard';
import StepNavigation from './components/StepNavigation';
import { FullScreenLoader } from './components/LoadingIndicator';
import PerformancePage from './components/performance/PerformancePage';
import AuthPage from './components/auth/AuthPage';
import PrivateRoute from './components/auth/PrivateRoute';
import { t } from './utils/i18n';

const { Header, Content, Footer, Sider } = Layout;

const VIEW = {
  STUDIO: 'studio',
  ASSETS: 'assets',
  PERFORMANCE: 'performance',
};

const StudioWorkspace = ({ onScriptGenerated, onVideoCreated, onStepChange }) => {
  const { state } = useAppContext();
  const { app, project } = state;

  return (
    <>
      <StepNavigation onStepChange={onStepChange} />
      <div className="avm-panel avm-panel-body">
        <div className="main-content">
          {app.currentStep === 0 && (
            <div className="step-content">
              <OptimizedScriptGenerator onScriptGenerated={onScriptGenerated} />
            </div>
          )}
          {app.currentStep >= 1 && app.currentStep <= 3 && (
            <div className="step-content">
              {app.currentStep === 1 && (
                <Alert
                  message="配置视频"
                  description="选择模板、语音与样式后，可在右上角进入「制作」与「导出」步骤。"
                  type="info"
                  showIcon
                  closable
                  style={{ marginBottom: 16 }}
                />
              )}
              <VideoPreview
                script={project.script}
                onVideoCreated={onVideoCreated}
              />
            </div>
          )}
        </div>
      </div>
    </>
  );
};

const AppShell = () => {
  const { state, actions } = useAppContext();
  const { app, project } = state;
  const { logout } = useAuth();
  const screens = Grid.useBreakpoint();
  const isNarrow = !screens.md;

  const [view, setView] = useState(VIEW.STUDIO);
  const [userDrawerOpen, setUserDrawerOpen] = useState(false);

  const handleScriptGenerated = (generatedScript) => {
    actions.setScript(generatedScript);
    actions.setCurrentStep(1);
    actions.addNotification('脚本已生成，请继续配置视频', 'success');
  };

  const handleVideoCreated = (createdVideoId) => {
    actions.setVideoId(createdVideoId);
    actions.setCurrentStep(3);
    actions.addNotification('视频制作完成，可以下载了', 'success');
  };

  const handleStepChange = (step) => {
    actions.setCurrentStep(step);
  };

  const mainCta = useMemo(() => {
    if (view !== VIEW.STUDIO) return null;
    if (app.currentStep === 0) return null;
    if (app.currentStep === 1) {
      return (
        <Tooltip title="配置完成后开始制作视频">
          <Button
            type="primary"
            size="middle"
            icon={<PlayCircleOutlined />}
            onClick={() => actions.setCurrentStep(2)}
            disabled={!project.script}
          >
            开始制作
          </Button>
        </Tooltip>
      );
    }
    if (app.currentStep === 2) {
      return (
        <Tooltip title="进入导出与下载">
          <Button
            type="primary"
            size="middle"
            icon={<PlayCircleOutlined />}
            onClick={() => actions.setCurrentStep(3)}
          >
            前往导出
          </Button>
        </Tooltip>
      );
    }
    if (app.currentStep === 3) {
      return (
        <Tooltip title="在页面下方使用下载功能">
          <Button type="primary" size="middle" icon={<DownloadOutlined />}>
            下载视频
          </Button>
        </Tooltip>
      );
    }
    return null;
  }, [view, app.currentStep, project.script, actions]);

  const menuItems = [
    {
      key: VIEW.STUDIO,
      icon: <VideoCameraOutlined />,
      label: '工作台',
    },
    {
      key: VIEW.ASSETS,
      icon: <AppstoreOutlined />,
      label: '资源库',
    },
    {
      key: VIEW.PERFORMANCE,
      icon: <BarChartOutlined />,
      label: '性能',
    },
  ];

  const moreMenu = {
    items: [
      {
        key: 'performance',
        label: t('header.performance'),
        icon: <DashboardOutlined />,
        onClick: () => setView(VIEW.PERFORMANCE),
      },
      {
        key: 'user',
        label: t('header.user'),
        icon: <UserOutlined />,
        onClick: () => setUserDrawerOpen(true),
      },
      { key: 'settings', label: t('header.settings'), icon: <SettingOutlined /> },
      { key: 'help', label: t('header.help'), icon: <QuestionCircleOutlined /> },
      { type: 'divider' },
      {
        key: 'logout',
        label: t('header.logout'),
        icon: <LogoutOutlined />,
        onClick: logout,
      },
    ],
  };

  const centerContent = () => {
    if (view === VIEW.PERFORMANCE) {
      return <PerformancePage onBack={() => setView(VIEW.STUDIO)} />;
    }
    if (view === VIEW.ASSETS) {
      return (
        <div className="avm-panel avm-panel-body">
          <div className="asset-manager-content">
            <StandaloneAssetManager />
          </div>
        </div>
      );
    }
    return (
      <StudioWorkspace
        onScriptGenerated={handleScriptGenerated}
        onVideoCreated={handleVideoCreated}
        onStepChange={handleStepChange}
      />
    );
  };

  return (
    <Layout className="avm-app">
      <Header className="avm-header">
        <div className="avm-header-inner">
          <button
            type="button"
            className="avm-brand"
            onClick={() => setView(VIEW.STUDIO)}
            style={{
              border: 'none',
              background: 'none',
              padding: 0,
              cursor: 'pointer',
              textAlign: 'left',
            }}
          >
            <span className="avm-brand-mark" aria-hidden>
              ▶
            </span>
            <span className="avm-brand-text">
              <span className="avm-brand-title">AI 短视频工作台</span>
              <span className="avm-brand-sub">脚本 · 配置 · 成片</span>
            </span>
          </button>
          <Space size="middle" wrap className="avm-header-actions" align="center">
            {isNarrow ? (
              <Segmented
                size="small"
                value={view}
                onChange={setView}
                options={[
                  { label: '工作台', value: VIEW.STUDIO },
                  { label: '资源', value: VIEW.ASSETS },
                  { label: '性能', value: VIEW.PERFORMANCE },
                ]}
              />
            ) : null}
            {mainCta}
            <Badge dot={project.isDirty} offset={[-2, 2]}>
              <Button
                type={view === VIEW.ASSETS ? 'primary' : 'default'}
                icon={<FolderOutlined />}
                onClick={() =>
                  setView(view === VIEW.ASSETS ? VIEW.STUDIO : VIEW.ASSETS)
                }
              >
                资源库
              </Button>
            </Badge>
            <Dropdown menu={moreMenu} placement="bottomRight" trigger={['click']}>
              <Button icon={<MoreOutlined />} type="text">
                更多
              </Button>
            </Dropdown>
          </Space>
        </div>
      </Header>

      <Layout className="avm-body">
        {!isNarrow ? (
          <Sider className="avm-sider" width={220} theme="light" style={{ background: 'transparent' }}>
            <div className="avm-sider-inner">
              <div className="avm-sider-card">
                <Menu
                  mode="inline"
                  selectedKeys={[view]}
                  items={menuItems}
                  onClick={({ key }) => setView(key)}
                />
              </div>
            </div>
          </Sider>
        ) : null}
        <Content className="avm-main-wrap">{centerContent()}</Content>
      </Layout>

      <Footer className="avm-footer">
        <span>AI 短视频制作平台 · {new Date().getFullYear()}</span>
        {project.isDirty ? (
          <span className="avm-footer-hint">项目有未保存更改</span>
        ) : null}
      </Footer>

      <Drawer
        title="用户中心"
        placement="right"
        width={440}
        onClose={() => setUserDrawerOpen(false)}
        open={userDrawerOpen}
        destroyOnClose
      >
        <UserDashboard />
      </Drawer>

      <FullScreenLoader
        visible={app.loading}
        title="处理中"
        description="请稍候"
        showProgress={false}
      />
    </Layout>
  );
};

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage />} />
      <Route path="/register" element={<AuthPage initialTab="register" />} />
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <AppShell />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AppProvider>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </AppProvider>
    </Router>
  );
}

export default App;
