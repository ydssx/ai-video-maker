import React, { useState, useEffect } from 'react';
import { Button, Card, Alert, Row, Col, message } from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import TemplateSelector from './TemplateSelector';
import VoiceSelector from './VoiceSelector';
import PresetManager from './PresetManager';
import { VideoGeneratingLoader } from './LoadingStates';

function VideoPreview({ script, onVideoCreated }) {
  const [loading, setLoading] = useState(false);
  const [videoId, setVideoId] = useState(null);
  const [videoStatus, setVideoStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('default');
  const [voiceConfig, setVoiceConfig] = useState({
    provider: 'gtts',
    voice: 'zh',
    speed: 1.0,
    enabled: true
  });

  useEffect(() => {
    let interval;
    if (videoId && videoStatus !== 'completed' && videoStatus !== 'failed') {
      interval = setInterval(checkVideoStatus, 2000);
    }
    return () => clearInterval(interval);
  }, [videoId, videoStatus]);

  useEffect(() => {
    // 加载模板列表
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await axios.get('/api/video/templates');
      setTemplates(response.data.templates);
    } catch (error) {
      console.error('获取模板失败:', error);
    }
  };

  const checkVideoStatus = async () => {
    try {
      const response = await axios.get(`/api/video/status/${videoId}`);
      setVideoStatus(response.data.status);
      
      if (response.data.status === 'completed') {
        setProgress(100);
        onVideoCreated(videoId);
      } else if (response.data.status === 'processing') {
        setProgress(prev => Math.min(prev + 10, 90));
      }
    } catch (error) {
      console.error('获取视频状态失败:', error);
    }
  };

  const getVideoStep = (progress) => {
    if (progress < 20) return 'download';
    if (progress < 40) return 'text';
    if (progress < 60) return 'voice';
    if (progress < 80) return 'compose';
    return 'export';
  };

  const handleApplyPreset = (preset) => {
    // 应用预设配置
    setSelectedTemplate(preset.template_id);
    setVoiceConfig(preset.voice_config);
    message.success(`已应用预设：${preset.name}`);
  };

  const handleCreateVideo = async () => {
    setLoading(true);
    setProgress(10);
    
    try {
      const response = await axios.post('/api/video/create', {
        script: script,
        template_id: selectedTemplate,
        voice_config: voiceConfig
      });
      
      setVideoId(response.data.video_id);
      setVideoStatus('processing');
      setProgress(20);
      
      // 记录统计
      try {
        await axios.post('/api/stats/record-video', null, {
          params: {
            duration: script.total_duration
          }
        });
      } catch (error) {
        console.warn('记录统计失败:', error);
      }
    } catch (error) {
      console.error('视频创建失败:', error);
      setLoading(false);
    }
  };

  if (!script) {
    return (
      <Alert
        message="请先生成脚本"
        description="您需要先在上一步生成视频脚本，然后才能创建视频。"
        type="info"
        showIcon
      />
    );
  }

  return (
    <div className="video-preview">
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card title="快速预设">
            <PresetManager 
              currentConfig={{
                template_id: selectedTemplate,
                voice_config: voiceConfig
              }}
              onApplyPreset={handleApplyPreset}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="视频模板选择">
            <TemplateSelector 
              selectedTemplate={selectedTemplate}
              onTemplateChange={setSelectedTemplate}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={12}>
          <VoiceSelector 
            voiceConfig={voiceConfig}
            onVoiceConfigChange={setVoiceConfig}
          />
        </Col>
        
        <Col span={12}>
          <Card title="制作设置" size="small">
            <p><strong>分辨率：</strong>1280x720</p>
            <p><strong>帧率：</strong>24fps</p>
            <p><strong>格式：</strong>MP4</p>
            <p><strong>选中模板：</strong>{templates.find(t => t.id === selectedTemplate)?.name || '默认模板'}</p>
            <p><strong>语音：</strong>{voiceConfig.enabled ? '已启用' : '已关闭'}</p>
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="脚本信息" size="small">
            <p><strong>标题：</strong>{script.title}</p>
            <p><strong>总时长：</strong>{script.total_duration}秒</p>
            <p><strong>场景数：</strong>{script.scenes.length}</p>
            <p><strong>风格：</strong>{script.style}</p>
          </Card>
        </Col>
      </Row>

      {!videoId && (
        <div style={{ textAlign: 'center', marginTop: 40 }}>
          <Button
            type="primary"
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={handleCreateVideo}
            loading={loading}
          >
            开始制作视频
          </Button>
        </div>
      )}

      {videoId && videoStatus !== 'completed' && (
        <div style={{ marginTop: 20 }}>
          <VideoGeneratingLoader 
            progress={progress}
            currentStep={getVideoStep(progress)}
          />
        </div>
      )}

      {videoStatus === 'completed' && (
        <Card style={{ marginTop: 20 }}>
          <div style={{ textAlign: 'center' }}>
            <Alert
              message="视频制作完成！"
              description="您的视频已经制作完成，可以预览和下载了。"
              type="success"
              showIcon
              style={{ marginBottom: 20 }}
            />
            
            <video 
              className="video-player"
              controls 
              width="600"
              src={`/output/${videoId}.mp4`}
              onError={(e) => {
                console.error('视频加载失败:', e);
                message.error('视频预览加载失败，但您仍可以尝试下载');
              }}
              onLoadStart={() => {
                console.log('开始加载视频');
              }}
              onCanPlay={() => {
                console.log('视频可以播放');
              }}
            >
              您的浏览器不支持视频播放。
            </video>
          </div>
        </Card>
      )}

      {videoStatus === 'failed' && (
        <Alert
          message="视频制作失败"
          description="视频制作过程中出现错误，请重试。"
          type="error"
          showIcon
          style={{ marginTop: 20 }}
          action={
            <Button size="small" onClick={handleCreateVideo}>
              重试
            </Button>
          }
        />
      )}
    </div>
  );
}

export default VideoPreview;