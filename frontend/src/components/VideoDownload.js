import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Button, 
  Space, 
  message, 
  Modal, 
  QRCode, 
  Input,
  Tooltip,
  Tag,
  Row,
  Col,
  Alert
} from 'antd';
import { 
  DownloadOutlined, 
  ShareAltOutlined, 
  QrcodeOutlined,
  CopyOutlined,
  CloudDownloadOutlined,
  LinkOutlined
} from '@ant-design/icons';
import axios from 'axios';

function VideoDownload({ videoId, onNewVideo }) {
  const [downloadUrl, setDownloadUrl] = useState('');
  const [cloudDownloadUrl, setCloudDownloadUrl] = useState('');
  const [storageType, setStorageType] = useState('local');
  const [shareModalVisible, setShareModalVisible] = useState(false);
  const [qrModalVisible, setQrModalVisible] = useState(false);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (videoId) {
      checkVideoStatus();
    }
  }, [videoId]);

  const checkVideoStatus = async () => {
    try {
      const response = await axios.get(`/api/video/status/${videoId}`);
      if (response.data.status === 'completed') {
        setDownloadUrl(response.data.download_url);
        setCloudDownloadUrl(response.data.cloud_download_url);
        setStorageType(response.data.storage_type || 'local');
      }
    } catch (error) {
      console.error('获取视频状态失败:', error);
    }
  };

  const handleDownload = async (useCloud = false) => {
    setDownloading(true);
    try {
      const url = useCloud && cloudDownloadUrl ? cloudDownloadUrl : downloadUrl;
      
      // 创建下载链接
      const link = document.createElement('a');
      link.href = url;
      link.download = `ai_video_${videoId}.mp4`;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      message.success('开始下载视频');
    } catch (error) {
      console.error('下载失败:', error);
      message.error('下载失败，请重试');
    } finally {
      setDownloading(false);
    }
  };

  const handleCopyLink = async () => {
    try {
      const shareUrl = `${window.location.origin}/output/${videoId}.mp4`;
      await navigator.clipboard.writeText(shareUrl);
      message.success('视频链接已复制到剪贴板');
    } catch (error) {
      message.error('复制失败，请手动复制链接');
    }
  };

  const handleShare = async () => {
    try {
      const shareUrl = `${window.location.origin}/output/${videoId}.mp4`;
      
      if (navigator.share) {
        await navigator.share({
          title: 'AI 生成的视频',
          text: '查看我用 AI 制作的视频',
          url: shareUrl
        });
      } else {
        setShareModalVisible(true);
      }
    } catch (error) {
      setShareModalVisible(true);
    }
  };

  const getVideoUrl = () => {
    return `${window.location.origin}/output/${videoId}.mp4`;
  };

  const getVideoSize = () => {
    // 这里可以从API获取实际文件大小
    return '约 5-15 MB';
  };

  const getVideoInfo = () => {
    return {
      format: 'MP4',
      resolution: '1280x720',
      fps: '24',
      codec: 'H.264',
      audio: 'AAC'
    };
  };

  const videoInfo = getVideoInfo();

  return (
    <Card title="视频下载" style={{ marginTop: 20 }}>
      {/* 视频信息 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        <Col span={12}>
          <div>
            <h4>视频信息</h4>
            <p><strong>格式:</strong> {videoInfo.format}</p>
            <p><strong>分辨率:</strong> {videoInfo.resolution}</p>
            <p><strong>帧率:</strong> {videoInfo.fps} fps</p>
            <p><strong>大小:</strong> {getVideoSize()}</p>
          </div>
        </Col>
        <Col span={12}>
          <div>
            <h4>存储状态</h4>
            <Space direction="vertical">
              <div>
                <Tag color={storageType === 'cloud' ? 'green' : 'blue'}>
                  {storageType === 'cloud' ? '云存储' : '本地存储'}
                </Tag>
                {cloudDownloadUrl && (
                  <Tag color="orange">云端备份可用</Tag>
                )}
              </div>
              <div style={{ fontSize: 12, color: '#666' }}>
                {storageType === 'cloud' 
                  ? '视频已上传到云存储，下载速度更快' 
                  : '视频存储在本地服务器'}
              </div>
            </Space>
          </div>
        </Col>
      </Row>

      {/* 下载按钮 */}
      <div style={{ textAlign: 'center', marginBottom: 20 }}>
        <Space size="large">
          <Button
            type="primary"
            size="large"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(false)}
            loading={downloading}
          >
            下载视频
          </Button>
          
          {cloudDownloadUrl && (
            <Button
              type="primary"
              size="large"
              icon={<CloudDownloadOutlined />}
              onClick={() => handleDownload(true)}
              loading={downloading}
              style={{ background: '#52c41a', borderColor: '#52c41a' }}
            >
              云端下载
            </Button>
          )}
          
          <Button
            size="large"
            icon={<ShareAltOutlined />}
            onClick={handleShare}
          >
            分享视频
          </Button>
          
          <Button
            size="large"
            icon={<QrcodeOutlined />}
            onClick={() => setQrModalVisible(true)}
          >
            二维码
          </Button>
        </Space>
      </div>

      {/* 快速操作 */}
      <div style={{ textAlign: 'center' }}>
        <Space>
          <Tooltip title="复制视频链接">
            <Button
              icon={<CopyOutlined />}
              onClick={handleCopyLink}
              size="small"
            >
              复制链接
            </Button>
          </Tooltip>
          
          <Tooltip title="在新标签页中打开">
            <Button
              icon={<LinkOutlined />}
              onClick={() => window.open(getVideoUrl(), '_blank')}
              size="small"
            >
              新窗口打开
            </Button>
          </Tooltip>
          
          <Button
            onClick={onNewVideo}
            size="small"
          >
            制作新视频
          </Button>
        </Space>
      </div>

      {/* 分享模态框 */}
      <Modal
        title="分享视频"
        open={shareModalVisible}
        onCancel={() => setShareModalVisible(false)}
        footer={null}
        width={400}
      >
        <div style={{ textAlign: 'center' }}>
          <p>复制链接分享给朋友：</p>
          <Input.Group compact>
            <Input
              value={getVideoUrl()}
              readOnly
              style={{ width: 'calc(100% - 80px)' }}
            />
            <Button
              type="primary"
              icon={<CopyOutlined />}
              onClick={handleCopyLink}
            >
              复制
            </Button>
          </Input.Group>
          
          <div style={{ marginTop: 20 }}>
            <Button
              icon={<QrcodeOutlined />}
              onClick={() => {
                setShareModalVisible(false);
                setQrModalVisible(true);
              }}
            >
              生成二维码
            </Button>
          </div>
        </div>
      </Modal>

      {/* 二维码模态框 */}
      <Modal
        title="视频二维码"
        open={qrModalVisible}
        onCancel={() => setQrModalVisible(false)}
        footer={null}
        width={300}
      >
        <div style={{ textAlign: 'center' }}>
          <QRCode value={getVideoUrl()} size={200} />
          <p style={{ marginTop: 16, color: '#666' }}>
            扫描二维码观看视频
          </p>
        </div>
      </Modal>

      {/* 提示信息 */}
      <Alert
        message="下载提示"
        description={
          <div>
            <p>• 视频文件为 MP4 格式，兼容所有主流播放器</p>
            <p>• 建议在 WiFi 环境下下载以节省流量</p>
            {cloudDownloadUrl && <p>• 云端下载速度更快，推荐使用</p>}
          </div>
        }
        type="info"
        showIcon
        style={{ marginTop: 16 }}
      />
    </Card>
  );
}

export default VideoDownload;