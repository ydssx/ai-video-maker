import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { Card, Button, Select, Alert, Descriptions, Space, message, Tooltip, Progress, Modal, Result, Tag } from 'antd';
import { 
  DownloadOutlined, 
  ShareAltOutlined, 
  CopyOutlined, 
  ReloadOutlined,
  MailOutlined,
  LinkOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import api from '../utils/api';
import { ProcessingLoader } from './LoadingIndicator';
import { t } from '../utils/i18n';

const { Option } = Select;

function VideoExport({ videoId }) {
  const [videoInfo, setVideoInfo] = useState(null);
  const [exportFormat, setExportFormat] = useState('mp4');
  const [quality, setQuality] = useState('medium');
  const [isPolling, setIsPolling] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [showFailureModal, setShowFailureModal] = useState(false);
  const [failureReason, setFailureReason] = useState('');
  const hasAnnouncedRef = useRef(false);
  const pollingIntervalRef = useRef(null);
  
  const qualityInfo = useMemo(() => ({
    low: { 
      label: '标清 (500k)', 
      note: '体积小，适合预览或弱网', 
      est: '~0.5MB/分钟',
      fileSize: '约 0.5MB/分钟'
    },
    medium: { 
      label: '高清 (1M)', 
      note: '通用推荐，清晰稳定', 
      est: '~1MB/分钟',
      fileSize: '约 1MB/分钟'
    },
    high: { 
      label: '超清 (2M)', 
      note: '更清晰，体积较大', 
      est: '~2MB/分钟',
      fileSize: '约 2MB/分钟'
    }
  }), []);

  // 获取视频信息
  const fetchVideoInfo = useCallback(async () => {
    try {
      const data = await api.get(`/video/status/${videoId}`);
      setVideoInfo(data);
      
      if (data.status === 'completed' && !hasAnnouncedRef.current) {
        hasAnnouncedRef.current = true;
        message.success('视频已准备就绪，可下载');
        stopPolling();
      }
      
      // 如果视频完成，检查文件是否真的存在
      if (data.status === 'completed' && data.preview_url) {
        try {
          await api.head(data.preview_url);
        } catch (error) {
          console.warn('视频文件可能不存在:', error);
          setFailureReason('视频文件可能还在处理中，请稍后再试');
          setShowFailureModal(true);
        }
      }
    } catch (error) {
      console.error('获取视频信息失败:', error);
      setFailureReason('获取视频信息失败，请检查网络连接');
      setShowFailureModal(true);
    }
  }, [videoId]);

  // 开始轮询
  const startPolling = useCallback(() => {
    if (pollingIntervalRef.current) return;
    
    setIsPolling(true);
    pollingIntervalRef.current = setInterval(async () => {
      await fetchVideoInfo();
    }, 3000);
  }, [fetchVideoInfo]);

  // 停止轮询
  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
      setIsPolling(false);
    }
  }, []);

  useEffect(() => {
    if (videoId) {
      fetchVideoInfo();
    }
  }, [videoId, fetchVideoInfo]);

  useEffect(() => {
    if (!videoId) return;
    
    const needPolling = !videoInfo || videoInfo.status !== 'completed';
    if (needPolling) {
      startPolling();
    } else {
      stopPolling();
    }

    return () => stopPolling();
  }, [videoId, videoInfo, startPolling, stopPolling]);

  // 处理下载
  const handleDownload = useCallback(async () => {
    if (!videoInfo || !videoInfo.download_url) {
      message.error('视频下载链接不可用');
      return;
    }

    try {
      setDownloadProgress(0);
      
      // 模拟下载进度
      const progressInterval = setInterval(() => {
        setDownloadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + Math.random() * 10;
        });
      }, 200);

      // 直接使用下载端点
      const link = document.createElement('a');
      link.href = videoInfo.download_url;
      link.download = `ai_video_${videoId}.${exportFormat}`;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setDownloadProgress(100);
      message.success('视频下载开始！');
      
      setTimeout(() => setDownloadProgress(0), 2000);
      
    } catch (error) {
      console.error('下载失败:', error);
      setFailureReason(`下载失败: ${error.message}`);
      setShowFailureModal(true);
    }
  }, [videoInfo, videoId, exportFormat]);

  // 处理复制链接
  const handleCopyLink = useCallback(async () => {
    if (videoInfo && videoInfo.download_url) {
      try {
        const isAbsolute = /^(http|https):\/\//i.test(videoInfo.download_url);
        const fullUrl = isAbsolute ? videoInfo.download_url : `${window.location.origin}${videoInfo.download_url}`;
        await navigator.clipboard.writeText(fullUrl);
        message.success('链接已复制到剪贴板');
      } catch (error) {
        console.error('复制失败:', error);
        message.error('复制失败，请手动复制链接');
      }
    } else {
      message.error('视频链接不可用');
    }
  }, [videoInfo]);

  // 处理分享
  const handleShare = useCallback(async () => {
    if (videoInfo && videoInfo.download_url) {
      try {
        if (navigator.share) {
          await navigator.share({
            title: 'AI制作的短视频',
            text: '使用AI短视频制作平台制作的精彩内容',
            url: videoInfo.download_url
          });
        } else {
          await handleCopyLink();
        }
      } catch (error) {
        console.error('分享失败:', error);
        message.error('分享失败');
      }
    } else {
      message.error('视频链接不可用');
    }
  }, [videoInfo, handleCopyLink]);

  // 处理重试
  const handleRetry = useCallback(() => {
    setShowFailureModal(false);
    setFailureReason('');
    fetchVideoInfo();
    startPolling();
  }, [fetchVideoInfo, startPolling]);

  // 处理稍后发送到邮箱
  const handleSendToEmail = useCallback(() => {
    message.info('功能开发中，请稍后再试');
    setShowFailureModal(false);
  }, []);

  // 渲染状态指示器
  const renderStatusIndicator = () => {
    if (!videoInfo) return null;

    switch (videoInfo.status) {
      case 'processing':
        return (
          <Alert
            message="视频处理中"
            description="正在生成您的视频，请稍候..."
            type="info"
            showIcon
            icon={<ProcessingLoader size="small" />}
            style={{ marginBottom: 16 }}
          />
        );
      case 'completed':
        return (
          <Alert
            message="视频已就绪"
            description="您的视频已制作完成，可以下载或分享了！"
            type="success"
            showIcon
            style={{ marginBottom: 16 }}
          />
        );
      case 'failed':
        return (
          <Alert
            message="视频生成失败"
            description="生成过程中遇到问题，请重试或联系技术支持"
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        );
      default:
        return null;
    }
  };

  // 渲染下载按钮
  const renderDownloadButton = () => {
    if (!videoInfo || videoInfo.status !== 'completed') {
      return (
        <Button 
          type="primary" 
          size="large" 
          icon={<DownloadOutlined />}
          disabled
        >
          等待视频生成完成
        </Button>
      );
    }

    return (
      <Button 
        type="primary" 
        size="large" 
        icon={<DownloadOutlined />}
        onClick={handleDownload}
        loading={downloadProgress > 0}
      >
        {downloadProgress > 0 ? '下载中...' : '下载视频'}
      </Button>
    );
  };

  if (!videoId) {
    return (
      <Card title="视频导出" size="small">
        <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
          请先生成视频
        </div>
      </Card>
    );
  }

  return (
    <>
      <Card title="视频导出" size="small">
        {/* 状态指示器 */}
        {renderStatusIndicator()}

        {/* 视频信息 */}
        {videoInfo && (
          <Descriptions title="视频信息" bordered size="small" style={{ marginBottom: 16 }}>
            <Descriptions.Item label="视频ID">{videoId}</Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={
                videoInfo.status === 'completed' ? 'success' : 
                videoInfo.status === 'processing' ? 'processing' : 'error'
              }>
                {videoInfo.status === 'completed' ? '已完成' : 
                 videoInfo.status === 'processing' ? '处理中' : '失败'}
              </Tag>
            </Descriptions.Item>
            {videoInfo.duration && (
              <Descriptions.Item label="时长">{videoInfo.duration}秒</Descriptions.Item>
            )}
            {videoInfo.resolution && (
              <Descriptions.Item label="分辨率">{videoInfo.resolution}</Descriptions.Item>
            )}
          </Descriptions>
        )}

        {/* 导出设置 */}
        <div style={{ marginBottom: 16 }}>
          <h4>导出设置</h4>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <label>格式：</label>
              <Select 
                value={exportFormat} 
                onChange={setExportFormat}
                style={{ width: 120, marginLeft: 8 }}
              >
                <Option value="mp4">MP4</Option>
                <Option value="avi">AVI</Option>
                <Option value="mov">MOV</Option>
              </Select>
            </div>
            
            <div>
              <label>质量：</label>
              <Select 
                value={quality} 
                onChange={setQuality}
                style={{ width: 200, marginLeft: 8 }}
              >
                {Object.entries(qualityInfo).map(([key, info]) => (
                  <Option key={key} value={key}>
                    {info.label} - {info.note} ({info.fileSize})
                  </Option>
                ))}
              </Select>
            </div>
          </Space>
        </div>

        {/* 下载进度 */}
        {downloadProgress > 0 && (
          <div style={{ marginBottom: 16 }}>
            <Progress 
              percent={downloadProgress} 
              status={downloadProgress === 100 ? 'success' : 'active'}
              format={(percent) => `${Math.round(percent)}%`}
            />
          </div>
        )}

        {/* 操作按钮 */}
        <div style={{ marginBottom: 16 }}>
          <Space>
            {renderDownloadButton()}
            
            {videoInfo && videoInfo.status === 'completed' && (
              <>
                <Button 
                  icon={<CopyOutlined />} 
                  onClick={handleCopyLink}
                  title="复制下载链接"
                >
                  复制链接
                </Button>
                
                <Button 
                  icon={<ShareAltOutlined />} 
                  onClick={handleShare}
                  title="分享视频"
                >
                  分享
                </Button>
              </>
            )}
          </Space>
        </div>

        {/* 轮询状态 */}
        {isPolling && (
          <div style={{ fontSize: '12px', color: '#666', textAlign: 'center' }}>
            <ReloadOutlined spin style={{ marginRight: 4 }} />
            正在检查视频状态...
          </div>
        )}
      </Card>

      {/* 失败处理模态框 */}
      <Modal
        title="视频处理遇到问题"
        open={showFailureModal}
        onCancel={() => setShowFailureModal(false)}
        footer={[
          <Button key="retry" type="primary" onClick={handleRetry} icon={<ReloadOutlined />}>
            重试
          </Button>,
          <Button key="email" onClick={handleSendToEmail} icon={<MailOutlined />}>
            稍后发送到邮箱
          </Button>,
          <Button key="cancel" onClick={() => setShowFailureModal(false)}>
            关闭
          </Button>
        ]}
      >
        <Result
          status="error"
          title="处理失败"
          subTitle={failureReason}
          extra={[
            <Button key="retry" type="primary" onClick={handleRetry}>
              重试
            </Button>
          ]}
        />
      </Modal>
    </>
  );
}

export default VideoExport;