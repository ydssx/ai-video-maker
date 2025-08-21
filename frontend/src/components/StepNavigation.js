import React from 'react';
import { Steps, Card, Button, Space, Progress, Tag, Tooltip } from 'antd';
import {
  FileTextOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  FolderOutlined
} from '@ant-design/icons';
import { useAppContext } from '../contexts/AppContext';

const { Step } = Steps;

const StepNavigation = ({ 
  onStepChange,
  showProgress = true,
  showQuickActions = true,
  compact = false
}) => {
  const { state, actions } = useAppContext();
  const { app, project, preview } = state;
  
  const steps = [
    {
      title: '生成脚本',
      icon: <FileTextOutlined />,
      description: '输入主题，AI自动生成视频脚本',
      key: 'script',
      requiredData: null,
      status: project.script ? 'finish' : app.currentStep === 0 ? 'process' : 'wait'
    },
    {
      title: '配置视频',
      icon: <SettingOutlined />,
      description: '选择模板、语音、样式等设置',
      key: 'config',
      requiredData: 'script',
      status: project.script ? 
        (app.currentStep === 1 ? 'process' : app.currentStep > 1 ? 'finish' : 'wait') : 
        'wait'
    },
    {
      title: '制作视频',
      icon: <PlayCircleOutlined />,
      description: '开始制作并预览视频',
      key: 'generate',
      requiredData: 'script',
      status: project.script ? 
        (app.currentStep === 2 ? 'process' : app.currentStep > 2 ? 'finish' : 'wait') : 
        'wait'
    },
    {
      title: '下载视频',
      icon: <DownloadOutlined />,
      description: '下载制作完成的视频',
      key: 'download',
      requiredData: 'video',
      status: project.videoId ? 
        (app.currentStep === 3 ? 'process' : 'finish') : 
        'wait'
    }
  ];
  
  // 检查步骤是否可访问
  const isStepAccessible = (stepIndex) => {
    const step = steps[stepIndex];
    
    switch (step.requiredData) {
      case 'script':
        return !!project.script;
      case 'video':
        return !!project.videoId;
      default:
        return true;
    }
  };
  
  // 获取步骤状态图标
  const getStepStatusIcon = (step, index) => {
    if (step.status === 'finish') {
      return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
    }
    
    if (step.status === 'process') {
      if (app.loading) {
        return <ClockCircleOutlined style={{ color: '#1890ff' }} />;
      }
      return step.icon;
    }
    
    if (!isStepAccessible(index)) {
      return <ExclamationCircleOutlined style={{ color: '#d9d9d9' }} />;
    }
    
    return step.icon;
  };
  
  // 处理步骤点击
  const handleStepClick = (stepIndex) => {
    if (!isStepAccessible(stepIndex)) {
      const step = steps[stepIndex];
      let message = '请先完成前置步骤';
      
      switch (step.requiredData) {
        case 'script':
          message = '请先生成视频脚本';
          break;
        case 'video':
          message = '请先制作视频';
          break;
      }
      
      actions.addNotification(message, 'warning');
      return;
    }
    
    actions.setCurrentStep(stepIndex);
    onStepChange && onStepChange(stepIndex);
  };
  
  // 快捷操作按钮
  const renderQuickActions = () => {
    if (!showQuickActions) return null;
    
    const currentStep = app.currentStep;
    const actions_list = [];
    
    // 根据当前步骤显示相关操作
    switch (currentStep) {
      case 0:
        actions_list.push(
          <Button key="templates" type="link" size="small">
            查看模板
          </Button>
        );
        break;
        
      case 1:
        if (project.script) {
          actions_list.push(
            <Button key="preview" type="link" size="small">
              快速预览
            </Button>
          );
        }
        break;
        
      case 2:
        if (project.script) {
          actions_list.push(
            <Button key="settings" type="link" size="small">
              导出设置
            </Button>
          );
        }
        break;
        
      case 3:
        if (project.videoId) {
          actions_list.push(
            <Button key="share" type="link" size="small">
              分享视频
            </Button>
          );
        }
        break;
    }
    
    if (actions_list.length === 0) return null;
    
    return (
      <div style={{ textAlign: 'center', marginTop: '12px' }}>
        <Space size="small">
          {actions_list}
        </Space>
      </div>
    );
  };
  
  // 进度信息
  const renderProgressInfo = () => {
    if (!showProgress) return null;
    
    const completedSteps = steps.filter(step => step.status === 'finish').length;
    const totalSteps = steps.length;
    const progressPercent = (completedSteps / totalSteps) * 100;
    
    return (
      <div style={{ marginBottom: '16px', textAlign: 'center' }}>
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <div style={{ color: '#666', fontSize: '12px' }}>
            制作进度: {completedSteps}/{totalSteps} 步骤
          </div>
          
          <Progress
            percent={progressPercent}
            size="small"
            showInfo={false}
            strokeColor="#1890ff"
          />
          
          <Space size="small">
            {project.script && <Tag color="green" size="small">✓ 脚本已生成</Tag>}
            {project.videoId && <Tag color="blue" size="small">✓ 视频已制作</Tag>}
            {project.isDirty && <Tag color="orange" size="small">● 未保存</Tag>}
            {preview.status === 'generating' && <Tag color="processing" size="small">制作中...</Tag>}
          </Space>
        </Space>
      </div>
    );
  };

  const getProgressPercent = () => {
    const completedSteps = steps.filter(step => step.status === 'finish').length;
    const totalSteps = steps.length;
    return (completedSteps / totalSteps) * 100;
  };
  
  // 紧凑模式
  if (compact) {
    return (
      <div style={{ padding: '8px 16px', borderBottom: '1px solid #f0f0f0' }}>
        <Space size="large" style={{ width: '100%', justifyContent: 'center' }}>
          {steps.map((step, index) => {
            const isActive = index === app.currentStep;
            const isAccessible = isStepAccessible(index);
            
            return (
              <Tooltip key={index} title={step.description}>
                <Button
                  type={isActive ? 'primary' : 'text'}
                  size="small"
                  icon={getStepStatusIcon(step, index)}
                  onClick={() => handleStepClick(index)}
                  disabled={!isAccessible}
                  style={{
                    opacity: isAccessible ? 1 : 0.5,
                    border: isActive ? '1px solid #1890ff' : 'none'
                  }}
                >
                  {step.title}
                </Button>
              </Tooltip>
            );
          })}
        </Space>
      </div>
    );
  }
  
  // 完整模式
  return (
    <div className="step-navigation-fixed">
      <div className="content-container">
        <Card className="steps-card" style={{ margin: 0, borderRadius: 0, borderLeft: 'none', borderRight: 'none' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <h3 style={{ margin: 0, marginRight: 16 }}>制作进度</h3>
              <Progress 
                percent={getProgressPercent()} 
                size="small" 
                style={{ width: 200 }}
                format={(percent) => `${Math.round(percent / 25)}/4 步骤`}
              />
            </div>
            
          </div>
          
          <Steps 
            current={app.currentStep} 
            size="small"
            style={{ marginBottom: 0 }}
          >
            {steps.map((step, index) => (
              <Step
                key={step.key}
                title={step.title}
                description={step.description}
                icon={getStepStatusIcon(step, index)}
                status={step.status}
                onClick={() => isStepAccessible(index) && onStepChange(index)}
                style={{ 
                  cursor: isStepAccessible(index) ? 'pointer' : 'default',
                  opacity: isStepAccessible(index) ? 1 : 0.6
                }}
              />
            ))}
          </Steps>
        </Card>
      </div>
    </div>
  );
};

export default StepNavigation;