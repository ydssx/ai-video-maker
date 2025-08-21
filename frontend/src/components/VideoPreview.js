import React, { useState, useEffect } from 'react';
import { Button, Card, Alert, Row, Col, message, Tabs } from 'antd';
import {
  PlayCircleOutlined,
  SettingOutlined,
  EditOutlined,
  SoundOutlined,
  SwapOutlined,
  DownloadOutlined,
  FolderOutlined
} from '@ant-design/icons';
import api from '../utils/api';
import { t } from '../utils/i18n';
import TemplateSelector from './TemplateSelector';
import VoiceSelector from './VoiceSelector';
import PresetManager from './PresetManager';
import VideoTimeline from './VideoTimeline';
import TextStyleEditor from './TextStyleEditor';
import AssetManager from './AssetManager';
import AudioManager from './AudioManager';
import TransitionEditor from './TransitionEditor';
import ExportSettings from './ExportSettings';
import ProjectManager from './ProjectManager';
import VideoDownload from './VideoDownload';
import { VideoGeneratingLoader } from './LoadingStates';

const { TabPane } = Tabs;

function VideoPreview({ script, onVideoCreated }) {
  const [loading, setLoading] = useState(false);
  const [videoId, setVideoId] = useState(null);
  const [videoStatus, setVideoStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('default');
  
  // 添加模板变化的调试信息
  useEffect(() => {
    console.log('选中的模板已变更:', selectedTemplate);
  }, [selectedTemplate]);
  const [voiceConfig, setVoiceConfig] = useState({
    provider: 'gtts',
    voice: 'zh',
    speed: 1.0,
    enabled: true
  });
  const [currentScene, setCurrentScene] = useState(0);
  const [textStyle, setTextStyle] = useState({
    fontFamily: 'Arial',
    fontSize: 48,
    fontColor: '#ffffff',
    position: 'center'
  });
  const [audioConfig, setAudioConfig] = useState(null);
  const [transitionConfig, setTransitionConfig] = useState([]);
  const [exportConfig, setExportConfig] = useState(null);
  const [currentProject, setCurrentProject] = useState(null);
  const [activeTab, setActiveTab] = useState('assets');

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
      const data = await api.get('/video/templates');
      setTemplates(data.templates);
    } catch (error) {
      console.error('获取模板失败:', error);
    }
  };

  const checkVideoStatus = async () => {
    try {
      const data = await api.get(`/video/status/${videoId}`);
      setVideoStatus(data.status);

      if (data.status === 'completed') {
        setProgress(100);
        onVideoCreated(videoId);
      } else if (data.status === 'processing') {
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

  const handleSceneChange = (sceneIndex) => {
    setCurrentScene(sceneIndex);
  };

  const handleTextStyleChange = (newStyle) => {
    setTextStyle(newStyle);
  };

  const handleAssetSelect = (asset) => {
    // 处理素材选择
    message.success(`已选择素材：${asset.name}`);
  };

  const handleAudioConfigChange = (config) => {
    setAudioConfig(config);
  };

  const handleTransitionChange = (transitions) => {
    setTransitionConfig(transitions);
  };

  const handleExportConfigChange = (config) => {
    setExportConfig(config);
  };

  const handleStartExport = (config) => {
    // 处理导出逻辑
    console.log('开始导出，配置:', config);
    message.info('开始导出视频...');
  };

  const handleProjectLoad = (project) => {
    setCurrentProject(project);
    // 这里可以加载项目的脚本和配置
    message.success(`已加载项目：${project.name}`);
  };

  const handleProjectSave = (project) => {
    setCurrentProject(project);
    message.success(`项目已保存：${project.name}`);
  };

  const handleDownloadVideo = async () => {
    try {
      // 创建下载链接
      const downloadUrl = `/api/video/download/${videoId}`;

      // 创建临时链接并触发下载
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `ai_video_${videoId}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      message.success('开始下载视频');
    } catch (error) {
      console.error('下载失败:', error);
      message.error('下载失败，请重试');
    }
  };

  const handleShareVideo = async () => {
    try {
      const shareUrl = `${window.location.origin}/output/${videoId}.mp4`;

      // 尝试使用 Web Share API
      if (navigator.share) {
        await navigator.share({
          title: t('preview.share.title', 'AI 生成的视频'),
          text: t('preview.share.text', '查看我用 AI 制作的视频'),
          url: shareUrl
        });
      } else {
        // 降级到复制链接
        await navigator.clipboard.writeText(shareUrl);
        message.success(t('preview.share.copied', '视频链接已复制到剪贴板'));
      }
    } catch (error) {
      console.error('分享失败:', error);
      // 手动复制链接作为备用方案
      const shareUrl = `${window.location.origin}/output/${videoId}.mp4`;
      try {
        await navigator.clipboard.writeText(shareUrl);
        message.success(t('preview.share.copied', '视频链接已复制到剪贴板'));
      } catch (clipboardError) {
        message.info(`${t('preview.share.link', '视频链接')}: ${shareUrl}`);
      }
    }
  };

  const handleCreateVideo = async () => {
    setLoading(true);
    setProgress(10);

    try {
      const response = await api.post('/video/create', {
        script: script,
        template_id: selectedTemplate,
        voice_config: voiceConfig,
        text_style: textStyle,
        audio_config: audioConfig,
        transition_config: transitionConfig,
        export_config: exportConfig
      });

      setVideoId(response.video_id);
      setVideoStatus('processing');
      setProgress(20);

      // 记录统计
      try {
        await api.post('/stats/record-video', null, {
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

  // 如果没有脚本，只显示素材管理和项目管理功能
  const hasScript = !!script;

  return (
    <div className="video-preview">
      {!hasScript && (
        <Alert
          message={t('preview.tip.title', '提示')}
          description={t('preview.tip.desc', '您可以先管理素材和项目，或者生成脚本后进行完整的视频制作。')}
          type="info"
          showIcon
          className="mb-24"
        />
      )}

      {hasScript && (
        <Row gutter={[24, 24]}>
          <Col span={24}>
            <Card title={t('preview.quickPreset', '快速预设')}>
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
      )}

      <Row gutter={[24, 24]} style={{ marginTop: hasScript ? 24 : 0 }}>
        <Col span={24}>
          <Card>
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
              {/* 始终可用的标签页 */}
              <TabPane
                tab="素材库"
                key="assets"
              >
                <AssetManager
                  onAssetSelect={handleAssetSelect}
                />
              </TabPane>

              <TabPane
                tab={
                  <span>
                    <SoundOutlined />
                    音频管理
                  </span>
                }
                key="audio"
              >
                <AudioManager
                  onAudioConfigChange={handleAudioConfigChange}
                />
              </TabPane>

              <TabPane
                tab={
                  <span>
                    <FolderOutlined />
                    项目管理
                  </span>
                }
                key="projects"
              >
                <ProjectManager
                  currentProject={currentProject}
                  onProjectLoad={handleProjectLoad}
                  onProjectSave={handleProjectSave}
                  script={script}
                  videoConfig={{
                    template_id: selectedTemplate,
                    voice_config: voiceConfig,
                    text_style: textStyle,
                    audio_config: audioConfig,
                    transition_config: transitionConfig,
                    export_config: exportConfig
                  }}
                />
              </TabPane>

              <TabPane
                tab={
                  <span>
                    <DownloadOutlined />
                    导出设置
                  </span>
                }
                key="export"
              >
                <ExportSettings
                  onExportConfigChange={handleExportConfigChange}
                  onStartExport={handleStartExport}
                />
              </TabPane>

              {/* 需要脚本的标签页 */}
              {hasScript && (
                <>
                  <TabPane
                    tab={
                      <span>
                        <SettingOutlined />
                        模板设置
                      </span>
                    }
                    key="template"
                  >
                    <TemplateSelector
                      selectedTemplate={selectedTemplate}
                      onTemplateChange={setSelectedTemplate}
                    />
                  </TabPane>

                  <TabPane
                    tab={
                      <span>
                        <EditOutlined />
                        文字样式
                      </span>
                    }
                    key="text"
                  >
                    <TextStyleEditor
                      textStyle={textStyle}
                      onStyleChange={handleTextStyleChange}
                    />
                  </TabPane>

                  <TabPane
                    tab={
                      <span>
                        <PlayCircleOutlined />
                        时间轴
                      </span>
                    }
                    key="timeline"
                  >
                    <VideoTimeline
                      script={script}
                      currentScene={currentScene}
                      onSceneChange={handleSceneChange}
                    />
                  </TabPane>

                  <TabPane
                    tab={
                      <span>
                        <SwapOutlined />
                        转场效果
                      </span>
                    }
                    key="transitions"
                  >
                    <TransitionEditor
                      script={script}
                      onTransitionChange={handleTransitionChange}
                    />
                  </TabPane>
                </>
              )}
            </Tabs>
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} className="mt-24">
        <Col span={12}>
          <VoiceSelector
            voiceConfig={voiceConfig}
            onVoiceConfigChange={setVoiceConfig}
          />
        </Col>

        <Col span={12}>
          <Card title={t('preview.settings', '制作设置')} size="small">
            <p><strong>分辨率：</strong>1280x720</p>
            <p><strong>帧率：</strong>24fps</p>
            <p><strong>格式：</strong>MP4</p>
            <p><strong>选中模板：</strong>{templates.find(t => t.id === selectedTemplate)?.name || '默认模板'}</p>
            <p><strong>语音：</strong>{voiceConfig.enabled ? '已启用' : '已关闭'}</p>
            <p><strong>当前场景：</strong>{currentScene + 1} / {script.scenes.length}</p>
          </Card>
        </Col>
      </Row>

      {!videoId && (
        <div className="text-center mt-40">
          <Button
            type="primary"
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={handleCreateVideo}
            loading={loading}
          >
            {t('preview.start', '开始制作视频')}
          </Button>
        </div>
      )}

      {videoId && videoStatus !== 'completed' && (
        <div className="mt-20">
          <VideoGeneratingLoader
            progress={progress}
            currentStep={getVideoStep(progress)}
          />
        </div>
      )}

      {videoStatus === 'completed' && (
        <div>
          <Card className="mt-20">
            <div className="text-center">
              <Alert
                message={t('preview.done.title', '视频制作完成！')}
                description={t('preview.done.desc', '您的视频已经制作完成，可以预览和下载了。')}
                type="success"
                showIcon
                className="mb-20"
              />

              <video
                className="video-player"
                controls
                width="600"
                src={`/output/${videoId}.mp4`}
                onError={(e) => {
                  console.error('视频加载失败:', e);
                  message.error(t('preview.video.failed', '视频预览加载失败，但您仍可以尝试下载'));
                }}
                onLoadStart={() => {
                  console.log(t('preview.video.loading', '开始加载视频'));
                }}
                onCanPlay={() => {
                  console.log(t('preview.video.canplay', '视频可以播放'));
                }}
              >
                {t('preview.video.notsupport', '您的浏览器不支持视频播放。')}
              </video>
            </div>
          </Card>

          <VideoDownload
            videoId={videoId}
            onNewVideo={() => {
              setVideoId(null);
              setVideoStatus(null);
              setProgress(0);
            }}
          />
        </div>
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