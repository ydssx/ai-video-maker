import React from 'react';
import { Spin, Progress, Card, Typography, Space } from 'antd';
import {
  LoadingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SyncOutlined
} from '@ant-design/icons';

const { Text, Title } = Typography;

const LoadingIndicator = ({
  loading = false,
  progress = 0,
  status = 'loading', // loading, success, error, processing
  title = '处理中...',
  description = '',
  showProgress = false,
  size = 'default', // small, default, large
  type = 'spin' // spin, progress, card
}) => {
  // 根据状态选择图标
  const getIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '24px' }} />;
      case 'error':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f', fontSize: '24px' }} />;
      case 'processing':
        return <SyncOutlined spin style={{ color: '#1890ff', fontSize: '24px' }} />;
      default:
        return <LoadingOutlined style={{ fontSize: '24px' }} />;
    }
  };
  
  // 根据状态选择颜色
  const getColor = () => {
    switch (status) {
      case 'success':
        return '#52c41a';
      case 'error':
        return '#ff4d4f';
      case 'processing':
        return '#1890ff';
      default:
        return '#1890ff';
    }
  };
  
  // 简单的旋转加载器
  if (type === 'spin') {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        padding: size === 'large' ? '40px' : size === 'small' ? '10px' : '20px'
      }}>
        <Space direction="vertical" align="center">
          <Spin 
            indicator={getIcon()} 
            spinning={loading || status === 'loading' || status === 'processing'}
            size={size}
          />
          {title && (
            <Text style={{ color: getColor(), fontSize: size === 'large' ? '16px' : '14px' }}>
              {title}
            </Text>
          )}
          {description && (
            <Text type="secondary" style={{ fontSize: '12px', textAlign: 'center' }}>
              {description}
            </Text>
          )}
        </Space>
      </div>
    );
  }
  
  // 进度条加载器
  if (type === 'progress') {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {title && (
            <Title level={4} style={{ margin: 0, color: getColor() }}>
              {title}
            </Title>
          )}
          
          <Progress
            percent={Math.round(progress)}
            status={status === 'error' ? 'exception' : status === 'success' ? 'success' : 'active'}
            strokeColor={getColor()}
            showInfo={showProgress}
            size={size}
          />
          
          {description && (
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {description}
            </Text>
          )}
          
          {showProgress && (
            <Text style={{ fontSize: '12px', color: getColor() }}>
              {progress.toFixed(1)}% 完成
            </Text>
          )}
        </Space>
      </div>
    );
  }
  
  // 卡片式加载器
  if (type === 'card') {
    return (
      <Card
        style={{
          textAlign: 'center',
          border: `1px solid ${getColor()}`,
          borderRadius: '8px',
          backgroundColor: status === 'error' ? '#fff2f0' : status === 'success' ? '#f6ffed' : '#f0f9ff'
        }}
        bodyStyle={{ padding: '24px' }}
      >
        <Space direction="vertical" align="center" size="large">
          <div style={{ fontSize: '48px' }}>
            {getIcon()}
          </div>
          
          {title && (
            <Title level={3} style={{ margin: 0, color: getColor() }}>
              {title}
            </Title>
          )}
          
          {showProgress && progress > 0 && (
            <Progress
              type="circle"
              percent={Math.round(progress)}
              status={status === 'error' ? 'exception' : status === 'success' ? 'success' : 'active'}
              strokeColor={getColor()}
              width={80}
            />
          )}
          
          {description && (
            <Text type="secondary" style={{ fontSize: '14px', maxWidth: '300px' }}>
              {description}
            </Text>
          )}
        </Space>
      </Card>
    );
  }
  
  return null;
};

// 预设的加载状态组件
export const ScriptGeneratingLoader = ({ progress = 0 }) => (
  <LoadingIndicator
    type="card"
    status="processing"
    title="AI正在生成脚本..."
    description="正在分析您的主题和风格偏好，生成个性化的视频脚本"
    showProgress={progress > 0}
    progress={progress}
  />
);

export const VideoGeneratingLoader = ({ progress = 0 }) => (
  <LoadingIndicator
    type="progress"
    status="processing"
    title="正在制作视频"
    description="正在合成视频场景、添加文字和音效，请稍候..."
    showProgress={true}
    progress={progress}
  />
);

export const FileUploadingLoader = ({ progress = 0, fileName = '' }) => (
  <LoadingIndicator
    type="progress"
    status="processing"
    title="上传文件中"
    description={fileName ? `正在上传: ${fileName}` : '正在上传文件，请稍候...'}
    showProgress={true}
    progress={progress}
  />
);

export const ProcessingLoader = ({ title = '处理中...', description = '' }) => (
  <LoadingIndicator
    type="spin"
    status="processing"
    title={title}
    description={description}
    size="large"
  />
);

export const SuccessIndicator = ({ title = '操作成功', description = '' }) => (
  <LoadingIndicator
    type="card"
    status="success"
    title={title}
    description={description}
  />
);

export const ErrorIndicator = ({ title = '操作失败', description = '' }) => (
  <LoadingIndicator
    type="card"
    status="error"
    title={title}
    description={description}
  />
);

// 全屏加载遮罩
export const FullScreenLoader = ({ 
  visible = false, 
  title = '加载中...', 
  description = '',
  progress = 0,
  showProgress = false
}) => {
  if (!visible) return null;
  
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 9999
    }}>
      <LoadingIndicator
        type="card"
        status="processing"
        title={title}
        description={description}
        showProgress={showProgress}
        progress={progress}
      />
    </div>
  );
};

export default LoadingIndicator;