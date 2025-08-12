import React, { useState } from 'react';
import { Layout, Steps, Card, Button, message, Progress, Row, Col, Drawer } from 'antd';
import { EditOutlined, PlayCircleOutlined, DownloadOutlined, CheckCircleOutlined, QuestionCircleOutlined, UserOutlined } from '@ant-design/icons';
import ScriptGenerator from './components/ScriptGenerator';
import VideoPreview from './components/VideoPreview';
import VideoExport from './components/VideoExport';
import { HelpModal } from './components/HelpTips';
import UserDashboard from './components/UserDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

const { Header, Content } = Layout;
const { Step } = Steps;

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [script, setScript] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [helpVisible, setHelpVisible] = useState(false);
  const [dashboardVisible, setDashboardVisible] = useState(false);

  const steps = [
    {
      title: '生成脚本',
      description: '输入主题，AI 生成视频脚本',
      icon: <EditOutlined />,
      content: <ScriptGenerator onScriptGenerated={handleScriptGenerated} />
    },
    {
      title: '制作视频',
      description: '选择模板和语音，制作视频',
      icon: <PlayCircleOutlined />,
      content: <VideoPreview script={script} onVideoCreated={handleVideoCreated} />
    },
    {
      title: '导出下载',
      description: '预览和下载完成的视频',
      icon: <DownloadOutlined />,
      content: <VideoExport videoId={videoId} />
    }
  ];

  function handleScriptGenerated(generatedScript) {
    setScript(generatedScript);
    setCurrentStep(1);
    message.success('脚本生成成功！');
  }

  function handleVideoCreated(id) {
    setVideoId(id);
    setCurrentStep(2);
    message.success('视频创建中...');
  }

  const next = () => {
    setCurrentStep(currentStep + 1);
  };

  const prev = () => {
    setCurrentStep(currentStep - 1);
  };

  return (
    <ErrorBoundary>
      <Layout className="layout">
      <Header style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
        padding: '0 50px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <Row justify="space-between" align="middle" style={{ height: '100%' }}>
          <Col>
            <h1 style={{ margin: 0, color: 'white', fontSize: '24px' }}>
              🎬 AI 短视频制作平台
            </h1>
          </Col>
          <Col>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <Button 
                type="text" 
                icon={<UserOutlined />}
                onClick={() => setDashboardVisible(true)}
                style={{ color: 'white' }}
              >
                我的数据
              </Button>
              <Button 
                type="text" 
                icon={<QuestionCircleOutlined />}
                onClick={() => setHelpVisible(true)}
                style={{ color: 'white' }}
              >
                帮助
              </Button>
              <div style={{ color: 'white', fontSize: '14px' }}>
                {script && videoId ? '已完成' : script ? '进行中' : '开始制作'}
                {script && videoId && <CheckCircleOutlined style={{ marginLeft: 8 }} />}
              </div>
            </div>
          </Col>
        </Row>
      </Header>
      <Content style={{ padding: '50px' }}>
        <div className="steps-content">
          {/* 进度指示器 */}
          <Card style={{ marginBottom: 24, background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)' }}>
            <Row gutter={24} align="middle">
              <Col span={18}>
                <Steps 
                  current={currentStep} 
                  size="small"
                  items={steps.map((step, index) => ({
                    title: step.title,
                    description: step.description,
                    icon: currentStep > index ? <CheckCircleOutlined /> : step.icon,
                    status: currentStep > index ? 'finish' : (currentStep === index ? 'process' : 'wait')
                  }))}
                />
              </Col>
              <Col span={6}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '12px', color: '#666', marginBottom: 4 }}>
                    总体进度
                  </div>
                  <Progress 
                    percent={Math.round(((currentStep + (script ? 0.5 : 0) + (videoId ? 0.5 : 0)) / 3) * 100)}
                    size="small"
                    status="active"
                  />
                </div>
              </Col>
            </Row>
          </Card>
          
          {/* 主要内容区域 */}
          <Card className="main-content-card">
            <div className="steps-content-wrapper">
              {steps[currentStep].content}
            </div>
            
            {/* 导航按钮 */}
            <div className="steps-action" style={{ marginTop: 24 }}>
              <Row justify="space-between" align="middle">
                <Col>
                  {currentStep > 0 && (
                    <Button 
                      size="large"
                      onClick={prev}
                      style={{ minWidth: 100 }}
                    >
                      上一步
                    </Button>
                  )}
                </Col>
                <Col>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: 4 }}>
                      第 {currentStep + 1} 步 / 共 {steps.length} 步
                    </div>
                    {currentStep < steps.length - 1 && (
                      <Button 
                        type="primary" 
                        size="large"
                        onClick={next} 
                        disabled={
                          (currentStep === 0 && !script) || 
                          (currentStep === 1 && !videoId)
                        }
                        style={{ minWidth: 120 }}
                      >
                        {currentStep === 0 ? '开始制作' : '继续下一步'}
                      </Button>
                    )}
                  </div>
                </Col>
                <Col>
                  {/* 占位，保持布局平衡 */}
                </Col>
              </Row>
            </div>
          </Card>
        </div>
      </Content>
      
      <HelpModal 
        visible={helpVisible}
        onClose={() => setHelpVisible(false)}
      />
      
      <Drawer
        title="我的数据统计"
        placement="right"
        onClose={() => setDashboardVisible(false)}
        open={dashboardVisible}
        width={400}
      >
        <UserDashboard />
      </Drawer>
    </Layout>
    </ErrorBoundary>
  );
}

export default App;