import React, { useState, useEffect } from 'react';
import { Card, Button, Select, Alert, Descriptions, Space, message } from 'antd';
import { DownloadOutlined, ShareAltOutlined, CopyOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Option } = Select;

function VideoExport({ videoId }) {
  const [videoInfo, setVideoInfo] = useState(null);
  const [exportFormat, setExportFormat] = useState('mp4');
  const [quality, setQuality] = useState('medium');

  useEffect(() => {
    if (videoId) {
      fetchVideoInfo();
    }
  }, [videoId]);

  const fetchVideoInfo = async () => {
    try {
      const response = await axios.get(`/api/video/status/${videoId}`);
      setVideoInfo(response.data);
      
      // 如果视频完成，检查文件是否真的存在
      if (response.data.status === 'completed' && response.data.preview_url) {
        try {
          await axios.head(response.data.preview_url);
        } catch (error) {
          console.warn('视频文件可能不存在:', error);
          message.warning('视频文件可能还在处理中，请稍后再试');
        }
      }
    } catch (error) {
      console.error('获取视频信息失败:', error);
      message.error('获取视频信息失败');
    }
  };

  const handleDownload = async () => {
    if (!videoInfo || !videoInfo.download_url) {
      message.error('视频下载链接不可用');
      return;
    }

    try {
      // 直接使用下载端点
      const link = document.createElement('a');
      link.href = videoInfo.download_url;
      link.download = `ai_video_${videoId}.${exportFormat}`;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      message.success('视频下载开始！');
      
    } catch (error) {
      console.error('下载失败:', error);
      message.error(`下载失败: ${error.message}`);
      
      // 备用方法：在新窗口打开
      try {
        window.open(videoInfo.download_url, '_blank');
        message.info('如果下载没有开始，请检查浏览器的下载设置');
      } catch (fallbackError) {
        console.error('备用下载方法也失败:', fallbackError);
        message.error('下载失败，请联系技术支持');
      }
    }
  };

  const handleCopyLink = async () => {
    if (videoInfo && videoInfo.download_url) {
      try {
        const fullUrl = `${window.location.origin}${videoInfo.download_url}`;
        await navigator.clipboard.writeText(fullUrl);
        message.success('链接已复制到剪贴板');
      } catch (error) {
        console.error('复制失败:', error);
        message.error('复制失败，请手动复制链接');
      }
    }
  };

  if (!videoId) {
    return (
      <Alert
        message="请先制作视频"
        description="您需要先完成视频制作，然后才能导出和下载。"
        type="info"
        showIcon
      />
    );
  }

  if (!videoInfo || videoInfo.status !== 'completed') {
    return (
      <Alert
        message="视频还未制作完成"
        description="请等待视频制作完成后再进行导出操作。"
        type="warning"
        showIcon
      />
    );
  }

  return (
    <div className="export-options">
      <Card title="视频信息">
        <Descriptions column={2} size="small">
          <Descriptions.Item label="视频ID">{videoId}</Descriptions.Item>
          <Descriptions.Item label="状态">制作完成</Descriptions.Item>
          <Descriptions.Item label="格式">MP4</Descriptions.Item>
          <Descriptions.Item label="分辨率">1280x720</Descriptions.Item>
          <Descriptions.Item label="帧率">24fps</Descriptions.Item>
          <Descriptions.Item label="编码">H.264</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="导出设置" style={{ marginTop: 20 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <label>导出格式：</label>
            <Select 
              value={exportFormat} 
              onChange={setExportFormat}
              style={{ width: 120, marginLeft: 8 }}
            >
              <Option value="mp4">MP4</Option>
              <Option value="mov">MOV</Option>
              <Option value="avi">AVI</Option>
            </Select>
          </div>
          
          <div>
            <label>视频质量：</label>
            <Select 
              value={quality} 
              onChange={setQuality}
              style={{ width: 120, marginLeft: 8 }}
            >
              <Option value="low">标清 (500k)</Option>
              <Option value="medium">高清 (1M)</Option>
              <Option value="high">超清 (2M)</Option>
            </Select>
          </div>
        </Space>
      </Card>

      <div className="download-section">
        <h3>下载您的视频</h3>
        <p>视频制作完成！您可以下载视频或分享给他人。</p>
        
        <Space size="large">
          <Button 
            type="primary" 
            size="large"
            icon={<DownloadOutlined />}
            onClick={handleDownload}
          >
            下载视频
          </Button>
          
          <Button 
            size="large"
            icon={<CopyOutlined />}
            onClick={handleCopyLink}
          >
            复制链接
          </Button>
          
          <Button 
            size="large"
            icon={<ShareAltOutlined />}
          >
            分享视频
          </Button>
        </Space>

        <Alert
          message="下载提示"
          description="视频文件较大，下载可能需要一些时间。建议在稳定的网络环境下进行下载。"
          type="info"
          showIcon
          style={{ marginTop: 20 }}
        />
      </div>
    </div>
  );
}

export default VideoExport;