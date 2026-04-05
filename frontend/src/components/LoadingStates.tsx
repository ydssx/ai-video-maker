import React from 'react';
import { Spin, Card, Progress, Typography } from 'antd';
import { LoadingOutlined, RocketOutlined, BulbOutlined, PlayCircleOutlined } from '@ant-design/icons';

const { Text } = Typography;

export const ScriptGeneratingLoader = ({ progress = 0 }) => {
  const messages = [
    "🤖 AI 正在分析您的主题...",
    "📝 生成创意脚本内容...",
    "🎬 优化场景和转场效果...",
    "✨ 完善脚本细节..."
  ];

  const currentMessage = messages[Math.floor((progress / 100) * messages.length)] || messages[0];

  return (
    <Card style={{ textAlign: 'center', padding: '40px 20px' }}>
      <div style={{ marginBottom: 24 }}>
        <Spin 
          indicator={<LoadingOutlined style={{ fontSize: 48, color: '#1890ff' }} spin />}
        />
      </div>
      <h3 style={{ color: '#1890ff', marginBottom: 16 }}>
        <BulbOutlined style={{ marginRight: 8 }} />
        正在生成脚本
      </h3>
      <Text type="secondary" style={{ fontSize: '16px', display: 'block', marginBottom: 20 }}>
        {currentMessage}
      </Text>
      <Progress 
        percent={progress} 
        status="active"
        strokeColor={{
          '0%': '#108ee9',
          '100%': '#87d068',
        }}
        style={{ maxWidth: 400, margin: '0 auto' }}
      />
    </Card>
  );
};

export const VideoGeneratingLoader = ({ progress = 0, currentStep = '' }) => {
  const steps = [
    { key: 'download', label: '下载素材图片', icon: '📥' },
    { key: 'text', label: '生成文字图层', icon: '📝' },
    { key: 'voice', label: '合成语音音频', icon: '🎵' },
    { key: 'compose', label: '合成视频画面', icon: '🎬' },
    { key: 'export', label: '导出最终视频', icon: '📤' }
  ];

  const currentStepIndex = steps.findIndex(step => step.key === currentStep);
  const stepProgress = currentStepIndex >= 0 ? ((currentStepIndex + 1) / steps.length) * 100 : progress;

  return (
    <Card style={{ textAlign: 'center', padding: '40px 20px' }}>
      <div style={{ marginBottom: 24 }}>
        <Spin 
          indicator={<PlayCircleOutlined style={{ fontSize: 48, color: '#1890ff' }} spin />}
        />
      </div>
      <h3 style={{ color: '#1890ff', marginBottom: 16 }}>
        <RocketOutlined style={{ marginRight: 8 }} />
        正在制作视频
      </h3>
      
      <div style={{ marginBottom: 24 }}>
        {steps.map((step, index) => (
          <div 
            key={step.key}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 12,
              opacity: index <= currentStepIndex ? 1 : 0.5,
              color: index === currentStepIndex ? '#1890ff' : '#666'
            }}
          >
            <span style={{ fontSize: '20px', marginRight: 12 }}>
              {step.icon}
            </span>
            <Text style={{ 
              fontSize: '14px',
              color: index === currentStepIndex ? '#1890ff' : '#666',
              fontWeight: index === currentStepIndex ? 'bold' : 'normal'
            }}>
              {step.label}
            </Text>
            {index === currentStepIndex && (
              <Spin size="small" style={{ marginLeft: 12 }} />
            )}
          </div>
        ))}
      </div>

      <Progress 
        percent={Math.max(progress, stepProgress)} 
        status="active"
        strokeColor={{
          '0%': '#108ee9',
          '100%': '#87d068',
        }}
        style={{ maxWidth: 400, margin: '0 auto' }}
      />
      
      <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: 16 }}>
        预计还需要 {Math.max(1, Math.ceil((100 - progress) / 10))} 分钟
      </Text>
    </Card>
  );
};

export const SimpleLoader = ({ message = "加载中...", icon = <LoadingOutlined /> }) => {
  return (
    <div style={{ textAlign: 'center', padding: '40px 20px' }}>
      <Spin indicator={React.cloneElement(icon, { style: { fontSize: 24, color: '#1890ff' } })} />
      <div style={{ marginTop: 16, color: '#666' }}>
        {message}
      </div>
    </div>
  );
};