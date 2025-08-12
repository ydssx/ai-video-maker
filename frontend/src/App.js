import React, { useState } from 'react';
import { Layout, Steps, Card, Button, message, Alert, Drawer } from 'antd';
import {
  FileTextOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  UserOutlined
} from '@ant-design/icons';
import ScriptGenerator from './components/ScriptGenerator';
import VideoPreview from './components/VideoPreview';
import StandaloneAssetManager from './components/StandaloneAssetManager';
import UserDashboard from './components/UserDashboard';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Step } = Steps;

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [script, setScript] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [showUserDashboard, setShowUserDashboard] = useState(false);

  const steps = [
    {
      title: '生成脚本',
      icon: <FileTextOutlined />,
      description: '输入主题，AI自动生成视频脚本'
    },
    {
      title: '配置视频',
      icon: <SettingOutlined />,
      description: '选择模板、语音、样式等设置'
    },
    {
      title: '制作视频',
      icon: <PlayCircleOutlined />,
      description: '开始制作并预览视频'
    },
    {
      title: '下载视频',
      icon: <DownloadOutlined />,
      description: '下载制作完成的视频'
    }
  ];

  const handleScriptGenerated = (generatedScript) => {
    setScript(generatedScript);
    setCurrentStep(1);
    message.success('脚本生成成功！现在可以配置视频设置了');
  };

  const handleVideoCreated = (createdVideoId) => {
    setVideoId(createdVideoId);
    setCurrentStep(3);
    message.success('视频制作完成！可以下载了');
  };

  // 检查步骤是否可访问
  const isStepAccessible = (stepIndex) => {
    switch (stepIndex) {
      case 0: return true; // 生成脚本始终可访问
      case 1: return !!script; // 配置视频需要脚本
      case 2: return !!script; // 制作视频需要脚本
      case 3: return !!videoId; // 下载视频需要视频ID
      default: return false;
    }
  };

  const handleStepChange = (step) => {
    if (!isStepAccessible(step)) {
      // 根据步骤给出不同的提示
      switch (step) {
        case 1:
        case 2:
          message.warning('请先生成视频脚本');
          break;
        case 3:
          message.warning('请先制作视频');
          break;
        default:
          message.warning('请按顺序完成步骤');
      }
      return;
    }

    // 只允许访问当前步骤或之前完成的步骤
    if (step <= currentStep || isStepAccessible(step)) {
      setCurrentStep(step);
    }
  };

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div className="header-content">
          <h1 style={{ color: 'white', margin: 0 }}>
            🎬 AI 短视频制作平台
          </h1>
          <div className="header-actions">
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
              onClick={() => setCurrentStep(currentStep === 4 ? 0 : 4)}
            >
              {currentStep === 4 ? '返回制作' : '资源管理'}
            </Button>
            <Button type="link" style={{ color: 'white' }}>
              帮助文档
            </Button>
          </div>
        </div>
      </Header>

      <Content className="app-content">
        <div className="content-container">
          {/* 步骤指示器 */}
          {currentStep !== 4 && (
            <Card className="steps-card">
              <div style={{ marginBottom: 16, textAlign: 'center', color: '#666' }}>
                <span>制作进度: {currentStep + 1}/4 步骤</span>
                {script && <span style={{ marginLeft: 16, color: '#52c41a' }}>✓ 脚本已生成</span>}
                {videoId && <span style={{ marginLeft: 16, color: '#52c41a' }}>✓ 视频已制作</span>}
              </div>
              <Steps
                current={currentStep}
                onChange={handleStepChange}
                type="navigation"
              >
                {steps.map((step, index) => {
                  const isAccessible = isStepAccessible(index);

                  // 判断步骤状态
                  let status = 'wait';
                  if (isAccessible && index < currentStep) {
                    status = 'finish';
                  } else if (index === currentStep) {
                    status = 'process';
                  } else if (!isAccessible) {
                    status = 'wait';
                  }

                  return (
                    <Step
                      key={index}
                      title={step.title}
                      description={step.description}
                      icon={step.icon}
                      status={status}
                      className={!isAccessible ? 'step-disabled' : ''}
                    />
                  );
                })}
              </Steps>
            </Card>
          )}

          {/* 主要内容区域 */}
          <div className="main-content">
            {currentStep === 0 && (
              <div>
                <ScriptGenerator onScriptGenerated={handleScriptGenerated} />
              </div>
            )}

            {currentStep >= 1 && currentStep <= 3 && (
              <div>
                {currentStep === 1 && (
                  <Alert
                    message="配置视频"
                    description="现在可以配置视频模板、样式、音频等设置，完成后点击'开始制作视频'。"
                    type="info"
                    showIcon
                    style={{ marginBottom: 16 }}
                  />
                )}
                <VideoPreview
                  script={script}
                  onVideoCreated={handleVideoCreated}
                />
              </div>
            )}

            {currentStep === 4 && (
              <StandaloneAssetManager />
            )}
          </div>
        </div>
      </Content>

      <Footer className="app-footer">
        <div style={{ textAlign: 'center' }}>
          AI 短视频制作平台 ©2024 - 让创作更简单
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
    </Layout>
  );
}

export default App;