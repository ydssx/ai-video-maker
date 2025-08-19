import React, { useState } from 'react';
import { Layout, Button, Alert, Drawer, Space, Badge, Menu } from 'antd';
import {
  UserOutlined,
  SettingOutlined,
  QuestionCircleOutlined,
  FolderOutlined,
  DashboardOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons';
import { AppProvider, useAppContext } from './contexts/AppContext';
import ScriptGenerator from './components/ScriptGenerator';
import VideoPreview from './components/VideoPreview';
import StandaloneAssetManager from './components/StandaloneAssetManager';
import UserDashboard from './components/UserDashboard';
import StepNavigation from './components/StepNavigation';
import { FullScreenLoader } from './components/LoadingIndicator';
import PerformancePage from './components/performance/PerformancePage';
import './App.css';

const { Header, Content, Footer } = Layout;

// 主应用内容组件
const AppContent = () => {
  const { state, actions } = useAppContext();
  const { app, project } = state;
  const [showUserDashboard, setShowUserDashboard] = useState(false);
  const [showAssetManager, setShowAssetManager] = useState(false);
  const [showPerformance, setShowPerformance] = useState(false);

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

  const renderMainContent = () => {
    if (showPerformance) {
      return (
        <PerformancePage onBack={() => setShowPerformance(false)} />
      );
    }

    return (
      <>
        {/* 步骤导航 */}
        {!showAssetManager && (
          <StepNavigation 
            onStepChange={handleStepChange}
            showProgress={true}
            showQuickActions={true}
          />
        )}

        {/* 主要内容区域 */}
        <div className="main-content">
          {!showAssetManager ? (
            <>
              {app.currentStep === 0 && (
                <div>
                  <ScriptGenerator onScriptGenerated={handleScriptGenerated} />
                </div>
              )}

              {app.currentStep >= 1 && app.currentStep <= 3 && (
                <div>
                  {app.currentStep === 1 && (
                    <Alert
                      message="配置视频"
                      description="现在可以配置视频模板、样式、音频等设置，完成后点击'开始制作视频'。"
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
            <div>
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
              
              <Button
                type="link"
                style={{ color: 'white' }}
                icon={<UserOutlined />}
                onClick={() => setShowUserDashboard(true)}
              >
                用户中心
              </Button>
              
              <Button
                type="link"
                style={{ color: 'white' }}
                icon={<SettingOutlined />}
              >
                设置
              </Button>
              
              <Button
                type="link"
                style={{ color: 'white' }}
                icon={<DashboardOutlined />}
                onClick={() => setShowPerformance(!showPerformance)}
              >
                {showPerformance ? '返回应用' : '性能监控'}
              </Button>
              <Button
                type="link"
                style={{ color: 'white' }}
                icon={<QuestionCircleOutlined />}
              >
                帮助
              </Button>
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
              ● 有未保存的更改
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
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;