import React from 'react';
import { Card, Button, Space, Tooltip, Divider, Typography } from 'antd';
import {
  SaveOutlined,
  UndoOutlined,
  RedoOutlined,
  EyeOutlined,
  DownloadOutlined,
  ShareAltOutlined,
  CopyOutlined,
  DeleteOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  FastForwardOutlined,
  BackwardOutlined
} from '@ant-design/icons';
import { useAppContext } from '../contexts/AppContext';

const { Text } = Typography;

const QuickActions = ({ 
  position = 'floating', // floating, inline, sidebar
  size = 'default',
  showLabels = false,
  customActions = []
}) => {
  const { state, actions } = useAppContext();
  const { app, project, editor, preview } = state;
  
  // 基础操作
  const baseActions = [
    {
      key: 'save',
      icon: <SaveOutlined />,
      label: '保存项目',
      tooltip: '保存当前项目 (Ctrl+S)',
      disabled: !project.isDirty,
      onClick: () => {
        actions.markProjectClean();
        actions.addNotification('项目已保存', 'success');
      }
    },
    {
      key: 'undo',
      icon: <UndoOutlined />,
      label: '撤销',
      tooltip: '撤销上一步操作 (Ctrl+Z)',
      disabled: true, // TODO: 实现撤销功能
      onClick: () => {
        // TODO: 实现撤销逻辑
      }
    },
    {
      key: 'redo',
      icon: <RedoOutlined />,
      label: '重做',
      tooltip: '重做上一步操作 (Ctrl+Y)',
      disabled: true, // TODO: 实现重做功能
      onClick: () => {
        // TODO: 实现重做逻辑
      }
    }
  ];
  
  // 预览操作
  const previewActions = [
    {
      key: 'preview',
      icon: <EyeOutlined />,
      label: '快速预览',
      tooltip: '预览当前视频',
      disabled: !project.script,
      onClick: () => {
        actions.setPreviewStatus('generating');
        actions.addNotification('开始生成预览...', 'info');
      }
    },
    {
      key: 'play',
      icon: editor.timeline.playing ? <PauseCircleOutlined /> : <PlayCircleOutlined />,
      label: editor.timeline.playing ? '暂停' : '播放',
      tooltip: `${editor.timeline.playing ? '暂停' : '播放'}预览 (空格键)`,
      disabled: !preview.url,
      onClick: () => {
        actions.updateTimeline({ playing: !editor.timeline.playing });
      }
    }
  ];
  
  // 导出操作
  const exportActions = [
    {
      key: 'download',
      icon: <DownloadOutlined />,
      label: '下载视频',
      tooltip: '下载制作完成的视频',
      disabled: !project.videoId,
      type: 'primary',
      onClick: () => {
        actions.addNotification('开始下载视频...', 'info');
      }
    },
    {
      key: 'share',
      icon: <ShareAltOutlined />,
      label: '分享',
      tooltip: '分享视频链接',
      disabled: !project.videoId,
      onClick: () => {
        // TODO: 实现分享功能
        actions.addNotification('分享链接已复制到剪贴板', 'success');
      }
    }
  ];
  
  // 编辑操作
  const editActions = [
    {
      key: 'copy',
      icon: <CopyOutlined />,
      label: '复制',
      tooltip: '复制选中内容 (Ctrl+C)',
      disabled: editor.selectedAssets.length === 0,
      onClick: () => {
        actions.addNotification('内容已复制', 'success');
      }
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: '删除',
      tooltip: '删除选中内容 (Delete)',
      disabled: editor.selectedAssets.length === 0,
      danger: true,
      onClick: () => {
        editor.selectedAssets.forEach(assetId => {
          actions.removeAsset(assetId);
        });
        actions.addNotification('已删除选中内容', 'success');
      }
    }
  ];
  
  // 播放控制操作
  const playbackActions = [
    {
      key: 'backward',
      icon: <BackwardOutlined />,
      label: '后退',
      tooltip: '后退5秒 (←)',
      disabled: !preview.url,
      onClick: () => {
        const newTime = Math.max(0, editor.timeline.currentTime - 5);
        actions.updateTimeline({ currentTime: newTime });
      }
    },
    {
      key: 'forward',
      icon: <FastForwardOutlined />,
      label: '前进',
      tooltip: '前进5秒 (→)',
      disabled: !preview.url,
      onClick: () => {
        const newTime = Math.min(editor.timeline.duration, editor.timeline.currentTime + 5);
        actions.updateTimeline({ currentTime: newTime });
      }
    }
  ];
  
  // 根据当前步骤选择显示的操作
  const getActionsForCurrentStep = () => {
    const currentStep = app.currentStep;
    let actions = [...baseActions];
    
    switch (currentStep) {
      case 0: // 脚本生成
        actions.push(...previewActions.filter(a => a.key === 'preview'));
        break;
        
      case 1: // 配置视频
        actions.push(...previewActions);
        actions.push(...editActions);
        break;
        
      case 2: // 制作视频
        actions.push(...previewActions);
        actions.push(...playbackActions);
        actions.push(...editActions);
        break;
        
      case 3: // 下载视频
        actions.push(...exportActions);
        actions.push(...previewActions);
        actions.push(...playbackActions);
        break;
    }
    
    // 添加自定义操作
    actions.push(...customActions);
    
    return actions;
  };
  
  const actionList = getActionsForCurrentStep();
  
  // 渲染按钮
  const renderButton = (action) => {
    const buttonProps = {
      key: action.key,
      icon: action.icon,
      size: size,
      type: action.type || 'default',
      danger: action.danger,
      disabled: action.disabled,
      onClick: action.onClick,
      loading: action.loading
    };
    
    const button = showLabels ? (
      <Button {...buttonProps}>
        {action.label}
      </Button>
    ) : (
      <Tooltip title={action.tooltip} key={action.key}>
        <Button {...buttonProps} />
      </Tooltip>
    );
    
    return button;
  };
  
  // 浮动面板样式
  if (position === 'floating') {
    return (
      <div style={{
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        zIndex: 1000,
        maxWidth: '400px'
      }}>
        <Card
          size="small"
          bodyStyle={{ padding: '8px 12px' }}
          style={{
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(8px)'
          }}
        >
          <Space size="small" wrap>
            {actionList.map(renderButton)}
          </Space>
          
          {project.isDirty && (
            <div style={{ marginTop: '8px', textAlign: 'center' }}>
              <Text type="warning" style={{ fontSize: '12px' }}>
                ● 有未保存的更改
              </Text>
            </div>
          )}
        </Card>
      </div>
    );
  }
  
  // 内联样式
  if (position === 'inline') {
    return (
      <div style={{ padding: '8px 0' }}>
        <Space size="small" wrap>
          {actionList.map(renderButton)}
        </Space>
      </div>
    );
  }
  
  // 侧边栏样式
  if (position === 'sidebar') {
    return (
      <Card
        title="快捷操作"
        size="small"
        style={{ marginBottom: '16px' }}
        bodyStyle={{ padding: '12px' }}
      >
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          {actionList.map(action => (
            <Button
              key={action.key}
              icon={action.icon}
              size={size}
              type={action.type || 'default'}
              danger={action.danger}
              disabled={action.disabled}
              onClick={action.onClick}
              loading={action.loading}
              block
            >
              {action.label}
            </Button>
          ))}
        </Space>
        
        {project.isDirty && (
          <>
            <Divider style={{ margin: '12px 0' }} />
            <Text type="warning" style={{ fontSize: '12px' }}>
              ● 有未保存的更改
            </Text>
          </>
        )}
      </Card>
    );
  }
  
  return null;
};

export default QuickActions;