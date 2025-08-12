import React, { useState } from 'react';
import { Card, Button, Space, Alert, Descriptions, message } from 'antd';
import { DownloadOutlined, PlayCircleOutlined, BugOutlined } from '@ant-design/icons';
import axios from 'axios';

function DownloadTest() {
  const [testVideo, setTestVideo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState(null);

  const createTestVideo = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/video/create-test-video');
      setTestVideo(response.data);
      message.success('测试视频创建成功！');
    } catch (error) {
      console.error('创建测试视频失败:', error);
      message.error('创建测试视频失败');
    } finally {
      setLoading(false);
    }
  };

  const downloadTestVideo = async () => {
    if (!testVideo || !testVideo.video_id) {
      message.error('没有可下载的测试视频');
      return;
    }

    try {
      // 方法1: 直接下载
      const downloadUrl = `/api/video/download/${testVideo.video_id}`;
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `test_video_${testVideo.video_id}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      message.success('下载开始！');
    } catch (error) {
      console.error('下载失败:', error);
      message.error('下载失败');
    }
  };

  const testDirectAccess = async () => {
    if (!testVideo || !testVideo.video_id) {
      message.error('没有可测试的视频');
      return;
    }

    try {
      // 测试直接访问
      const staticUrl = `/output/${testVideo.video_id}.mp4`;
      const response = await axios.head(staticUrl);
      message.success(`静态文件访问成功: ${response.status}`);
    } catch (error) {
      console.error('静态文件访问失败:', error);
      message.error(`静态文件访问失败: ${error.response?.status || error.message}`);
    }
  };

  const getDebugInfo = async () => {
    try {
      const response = await axios.get('/api/stats/debug/files');
      setDebugInfo(response.data);
      message.success('调试信息获取成功');
    } catch (error) {
      console.error('获取调试信息失败:', error);
      message.error('获取调试信息失败');
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <Card title="视频下载测试工具" style={{ marginBottom: 20 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Alert
            message="测试说明"
            description="这个工具用于测试视频下载功能。首先创建一个测试视频，然后尝试下载。"
            type="info"
            showIcon
          />

          <Space>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={createTestVideo}
              loading={loading}
            >
              创建测试视频
            </Button>

            <Button
              icon={<BugOutlined />}
              onClick={getDebugInfo}
            >
              获取调试信息
            </Button>
          </Space>

          {testVideo && (
            <Card title="测试视频信息" size="small">
              <Descriptions column={1} size="small">
                <Descriptions.Item label="视频ID">{testVideo.video_id}</Descriptions.Item>
                <Descriptions.Item label="状态">{testVideo.status}</Descriptions.Item>
                <Descriptions.Item label="文件路径">{testVideo.file_path}</Descriptions.Item>
                <Descriptions.Item label="文件存在">{testVideo.file_exists ? '是' : '否'}</Descriptions.Item>
              </Descriptions>

              <Space style={{ marginTop: 16 }}>
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  onClick={downloadTestVideo}
                >
                  下载测试视频
                </Button>

                <Button onClick={testDirectAccess}>
                  测试静态访问
                </Button>

                <Button
                  type="link"
                  onClick={() => window.open(`/output/${testVideo.video_id}.mp4`, '_blank')}
                >
                  在新窗口打开
                </Button>
              </Space>
            </Card>
          )}

          {debugInfo && (
            <Card title="文件系统调试信息" size="small">
              <Descriptions column={1} size="small">
                <Descriptions.Item label="输出目录路径">{debugInfo.output_dir.path}</Descriptions.Item>
                <Descriptions.Item label="输出目录存在">{debugInfo.output_dir.exists ? '是' : '否'}</Descriptions.Item>
                <Descriptions.Item label="输出目录文件">
                  {debugInfo.output_dir.files?.length > 0 ?
                    debugInfo.output_dir.files.join(', ') :
                    '无文件'
                  }
                </Descriptions.Item>
                <Descriptions.Item label="资源目录路径">{debugInfo.assets_dir.path}</Descriptions.Item>
                <Descriptions.Item label="资源目录存在">{debugInfo.assets_dir.exists ? '是' : '否'}</Descriptions.Item>
              </Descriptions>
            </Card>
          )}
        </Space>
      </Card>
    </div>
  );
}

export default DownloadTest;