import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Select, 
  Slider, 
  Row, 
  Col, 
  Switch, 
  InputNumber,
  Button,
  Alert,
  Progress,
  Divider,
  Tag,
  Tooltip,
  Space,
  message
} from 'antd';
import { 
  DownloadOutlined, 
  SettingOutlined,
  InfoCircleOutlined,
  CloudDownloadOutlined,
  FileImageOutlined,
  VideoCameraOutlined
} from '@ant-design/icons';
import { t } from '../utils/i18n';

const { Option } = Select;

function ExportSettings({ onExportConfigChange, onStartExport }) {
  const [exportConfig, setExportConfig] = useState({
    // 视频设置
    resolution: '1280x720',
    frameRate: 24,
    bitrate: 2000,
    format: 'mp4',
    codec: 'h264',
    
    // 音频设置
    audioCodec: 'aac',
    audioBitrate: 128,
    audioSampleRate: 44100,
    
    // 质量设置
    quality: 'high',
    preset: 'medium',
    
    // 高级设置
    enableHardwareAcceleration: true,
    twoPass: false,
    customFFmpegArgs: '',
    
    // 输出设置
    outputName: '',
    watermark: false,
    watermarkText: '',
    watermarkPosition: 'bottom-right',
    
    // 批量导出
    exportThumbnail: true,
    exportSubtitles: false,
    exportAudio: false
  });

  const [estimatedSize, setEstimatedSize] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState(0);
  const [exportProgress, setExportProgress] = useState(0);
  const [isExporting, setIsExporting] = useState(false);

  // 预设配置
  const qualityPresets = {
    'ultra': {
      name: t('export.preset.ultra', '超高清'),
      resolution: '1920x1080',
      bitrate: 8000,
      frameRate: 30,
      description: t('export.preset.ultra.desc', '最佳质量，文件较大'),
      color: 'red'
    },
    'high': {
      name: t('export.preset.high', '高清'),
      resolution: '1280x720',
      bitrate: 2000,
      frameRate: 24,
      description: t('export.preset.high.desc', '高质量，适合大多数用途'),
      color: 'orange'
    },
    'medium': {
      name: t('export.preset.medium', '标清'),
      resolution: '854x480',
      bitrate: 1000,
      frameRate: 24,
      description: t('export.preset.medium.desc', '中等质量，文件适中'),
      color: 'blue'
    },
    'low': {
      name: t('export.preset.low', '低清'),
      resolution: '640x360',
      bitrate: 500,
      frameRate: 20,
      description: t('export.preset.low.desc', '较小文件，快速导出'),
      color: 'green'
    }
  };

  const formatOptions = [
    { value: 'mp4', label: 'MP4', description: t('export.format.mp4', '通用格式，兼容性最好') },
    { value: 'mov', label: 'MOV', description: t('export.format.mov', 'Apple格式，质量较高') },
    { value: 'avi', label: 'AVI', description: t('export.format.avi', '传统格式，文件较大') },
    { value: 'webm', label: 'WebM', description: t('export.format.webm', '网络优化格式') },
    { value: 'mkv', label: 'MKV', description: t('export.format.mkv', '开源格式，功能丰富') }
  ];

  const codecOptions = [
    { value: 'h264', label: 'H.264', description: t('export.codec.h264', '标准编码，兼容性好') },
    { value: 'h265', label: 'H.265', description: t('export.codec.h265', '新编码，文件更小') },
    { value: 'vp9', label: 'VP9', description: t('export.codec.vp9', '开源编码，质量高') },
    { value: 'av1', label: 'AV1', description: t('export.codec.av1', '最新编码，效率最高') }
  ];

  useEffect(() => {
    // 估算文件大小和导出时间
    calculateEstimates();
    
    // 通知父组件配置变化
    onExportConfigChange && onExportConfigChange(exportConfig);
  }, [exportConfig]);

  const calculateEstimates = () => {
    const { resolution, bitrate, frameRate } = exportConfig;
    const [width, height] = resolution.split('x').map(Number);
    
    // 估算文件大小 (MB) = (bitrate * duration) / 8 / 1024
    // 假设视频时长为60秒
    const duration = 60;
    const sizeInMB = (bitrate * duration) / 8 / 1024;
    setEstimatedSize(sizeInMB);
    
    // 估算导出时间（基于分辨率和帧率）
    const complexity = (width * height * frameRate) / 1000000;
    const timeInSeconds = complexity * 2; // 简化计算
    setEstimatedTime(timeInSeconds);
  };

  const updateConfig = (key, value) => {
    setExportConfig(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const applyPreset = (presetKey) => {
    const preset = qualityPresets[presetKey];
    setExportConfig(prev => ({
      ...prev,
      quality: presetKey,
      resolution: preset.resolution,
      bitrate: preset.bitrate,
      frameRate: preset.frameRate
    }));
    message.success(t('export.preset.applied', '已应用预设') + `: ${preset.name}`);
  };

  const handleExport = () => {
    setIsExporting(true);
    setExportProgress(0);
    
    // 模拟导出进度
    const interval = setInterval(() => {
      setExportProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsExporting(false);
          message.success(t('export.done', '视频导出完成！'));
          return 100;
        }
        return prev + Math.random() * 10;
      });
    }, 500);
    
    // 调用父组件的导出函数
    onStartExport && onStartExport(exportConfig);
  };

  const resetToDefaults = () => {
    setExportConfig({
      resolution: '1280x720',
      frameRate: 24,
      bitrate: 2000,
      format: 'mp4',
      codec: 'h264',
      audioCodec: 'aac',
      audioBitrate: 128,
      audioSampleRate: 44100,
      quality: 'high',
      preset: 'medium',
      enableHardwareAcceleration: true,
      twoPass: false,
      customFFmpegArgs: '',
      outputName: '',
      watermark: false,
      watermarkText: '',
      watermarkPosition: 'bottom-right',
      exportThumbnail: true,
      exportSubtitles: false,
      exportAudio: false
    });
    message.success(t('export.reset', '已重置为默认设置'));
  };

  return (
    <div className="export-settings">
      {/* 快速预设 */}
      <Card title={t('export.preset.title', '质量预设')} style={{ marginBottom: 16 }}>
        <Row gutter={[8, 8]}>
          {Object.entries(qualityPresets).map(([key, preset]) => (
            <Col span={6} key={key}>
              <Card
                size="small"
                hoverable
                onClick={() => applyPreset(key)}
                style={{
                  border: exportConfig.quality === key ? '2px solid #1890ff' : '1px solid #d9d9d9',
                  cursor: 'pointer'
                }}
              >
                <div style={{ textAlign: 'center' }}>
                  <Tag color={preset.color} style={{ marginBottom: 8 }}>
                    {preset.name}
                  </Tag>
                  <div style={{ fontSize: 12, color: '#666' }}>
                    {preset.resolution}
                  </div>
                  <div style={{ fontSize: 12, color: '#666' }}>
                    {preset.bitrate}kbps
                  </div>
                  <div style={{ fontSize: 11, color: '#999', marginTop: 4 }}>
                    {preset.description}
                  </div>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      <Row gutter={[16, 16]}>
        {/* 视频设置 */}
        <Col span={12}>
          <Card title={<><VideoCameraOutlined /> {t('export.video.title', '视频设置')}</>}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.video.resolution', '分辨率:')}</div>
              <Select
                value={exportConfig.resolution}
                onChange={(value) => updateConfig('resolution', value)}
                style={{ width: '100%' }}
              >
                <Option value="3840x2160">{t('export.video.res.4k', '4K (3840x2160)')}</Option>
                <Option value="1920x1080">{t('export.video.res.1080p', '1080p (1920x1080)')}</Option>
                <Option value="1280x720">{t('export.video.res.720p', '720p (1280x720)')}</Option>
                <Option value="854x480">{t('export.video.res.480p', '480p (854x480)')}</Option>
                <Option value="640x360">{t('export.video.res.360p', '360p (640x360)')}</Option>
              </Select>
            </div>

            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.video.fps', '帧率')}: {exportConfig.frameRate} fps</div>
              <Slider
                min={15}
                max={60}
                value={exportConfig.frameRate}
                onChange={(value) => updateConfig('frameRate', value)}
                marks={{
                  15: '15',
                  24: '24',
                  30: '30',
                  60: '60'
                }}
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.video.bitrate', '码率')}: {exportConfig.bitrate} kbps</div>
              <Slider
                min={500}
                max={10000}
                step={100}
                value={exportConfig.bitrate}
                onChange={(value) => updateConfig('bitrate', value)}
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.video.format', '格式:')}</div>
              <Select
                value={exportConfig.format}
                onChange={(value) => updateConfig('format', value)}
                style={{ width: '100%' }}
              >
                {formatOptions.map(format => (
                  <Option key={format.value} value={format.value}>
                    <Tooltip title={format.description}>
                      {format.label}
                    </Tooltip>
                  </Option>
                ))}
              </Select>
            </div>

            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.video.codec', '编码器:')}</div>
              <Select
                value={exportConfig.codec}
                onChange={(value) => updateConfig('codec', value)}
                style={{ width: '100%' }}
              >
                {codecOptions.map(codec => (
                  <Option key={codec.value} value={codec.value}>
                    <Tooltip title={codec.description}>
                      {codec.label}
                    </Tooltip>
                  </Option>
                ))}
              </Select>
            </div>
          </Card>
        </Col>

        {/* 音频设置 */}
        <Col span={12}>
          <Card title={t('export.audio.title', '音频设置')}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.audio.codec', '音频编码:')}</div>
              <Select
                value={exportConfig.audioCodec}
                onChange={(value) => updateConfig('audioCodec', value)}
                style={{ width: '100%' }}
              >
                <Option value="aac">{t('export.audio.codec.aac', 'AAC (推荐)')}</Option>
                <Option value="mp3">MP3</Option>
                <Option value="opus">Opus</Option>
                <Option value="vorbis">Vorbis</Option>
              </Select>
            </div>

            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.audio.bitrate', '音频码率')}: {exportConfig.audioBitrate} kbps</div>
              <Slider
                min={64}
                max={320}
                step={32}
                value={exportConfig.audioBitrate}
                onChange={(value) => updateConfig('audioBitrate', value)}
                marks={{
                  64: '64',
                  128: '128',
                  192: '192',
                  320: '320'
                }}
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.audio.sampleRate', '采样率:')}</div>
              <Select
                value={exportConfig.audioSampleRate}
                onChange={(value) => updateConfig('audioSampleRate', value)}
                style={{ width: '100%' }}
              >
                <Option value={22050}>{t('export.audio.sample.22050', '22.05 kHz')}</Option>
                <Option value={44100}>{t('export.audio.sample.44100', '44.1 kHz (CD质量)')}</Option>
                <Option value={48000}>{t('export.audio.sample.48000', '48 kHz (专业)')}</Option>
                <Option value={96000}>{t('export.audio.sample.96000', '96 kHz (高保真)')}</Option>
              </Select>
            </div>

            <Divider />

            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.encode.preset', '编码预设:')}</div>
              <Select
                value={exportConfig.preset}
                onChange={(value) => updateConfig('preset', value)}
                style={{ width: '100%' }}
              >
                <Option value="ultrafast">{t('export.encode.preset.ultrafast', '极速 (质量最低)')}</Option>
                <Option value="fast">{t('export.encode.preset.fast', '快速')}</Option>
                <Option value="medium">{t('export.encode.preset.medium', '中等 (推荐)')}</Option>
                <Option value="slow">{t('export.encode.preset.slow', '慢速 (质量较高)')}</Option>
                <Option value="veryslow">{t('export.encode.preset.veryslow', '极慢 (质量最高)')}</Option>
              </Select>
            </div>

            <div style={{ marginBottom: 8 }}>
              <Switch
                checked={exportConfig.enableHardwareAcceleration}
                onChange={(checked) => updateConfig('enableHardwareAcceleration', checked)}
              />
              <span style={{ marginLeft: 8 }}>{t('export.hwaccel', '启用硬件加速')}</span>
            </div>

            <div>
              <Switch
                checked={exportConfig.twoPass}
                onChange={(checked) => updateConfig('twoPass', checked)}
              />
              <span style={{ marginLeft: 8 }}>{t('export.twopass', '两遍编码 (质量更好)')}</span>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 输出设置 */}
      <Card title={t('export.output.title', '输出设置')} style={{ marginTop: 16 }}>
        <Row gutter={[16, 16]}>
          <Col span={8}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.output.filename', '文件名:')}</div>
              <input
                type="text"
                placeholder={t('export.output.filename.placeholder', '留空使用默认名称')}
                value={exportConfig.outputName}
                onChange={(e) => updateConfig('outputName', e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '6px 12px', 
                  border: '1px solid #d9d9d9',
                  borderRadius: 4
                }}
              />
            </div>
          </Col>

          <Col span={8}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.output.watermark.position', '水印位置:')}</div>
              <Select
                value={exportConfig.watermarkPosition}
                onChange={(value) => updateConfig('watermarkPosition', value)}
                style={{ width: '100%' }}
                disabled={!exportConfig.watermark}
              >
                <Option value="top-left">{t('export.output.watermark.pos.tl', '左上角')}</Option>
                <Option value="top-right">{t('export.output.watermark.pos.tr', '右上角')}</Option>
                <Option value="bottom-left">{t('export.output.watermark.pos.bl', '左下角')}</Option>
                <Option value="bottom-right">{t('export.output.watermark.pos.br', '右下角')}</Option>
                <Option value="center">{t('export.output.watermark.pos.center', '居中')}</Option>
              </Select>
            </div>
          </Col>

          <Col span={8}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>{t('export.output.watermark.text', '水印文字:')}</div>
              <input
                type="text"
                placeholder={t('export.output.watermark.placeholder', '输入水印文字')}
                value={exportConfig.watermarkText}
                onChange={(e) => updateConfig('watermarkText', e.target.value)}
                disabled={!exportConfig.watermark}
                style={{ 
                  width: '100%', 
                  padding: '6px 12px', 
                  border: '1px solid #d9d9d9',
                  borderRadius: 4,
                  opacity: exportConfig.watermark ? 1 : 0.5
                }}
              />
            </div>
          </Col>
        </Row>

        <Row gutter={[16, 16]}>
          <Col span={6}>
            <Switch
              checked={exportConfig.watermark}
              onChange={(checked) => updateConfig('watermark', checked)}
            />
            <span style={{ marginLeft: 8 }}>{t('export.output.watermark.enable', '添加水印')}</span>
          </Col>

          <Col span={6}>
            <Switch
              checked={exportConfig.exportThumbnail}
              onChange={(checked) => updateConfig('exportThumbnail', checked)}
            />
            <span style={{ marginLeft: 8 }}>{t('export.output.thumb', '导出缩略图')}</span>
          </Col>

          <Col span={6}>
            <Switch
              checked={exportConfig.exportSubtitles}
              onChange={(checked) => updateConfig('exportSubtitles', checked)}
            />
            <span style={{ marginLeft: 8 }}>{t('export.output.subtitle', '导出字幕文件')}</span>
          </Col>

          <Col span={6}>
            <Switch
              checked={exportConfig.exportAudio}
              onChange={(checked) => updateConfig('exportAudio', checked)}
            />
            <span style={{ marginLeft: 8 }}>{t('export.output.audio', '导出音频文件')}</span>
          </Col>
        </Row>
      </Card>

      {/* 估算信息 */}
      <Card title={t('export.estimate.title', '导出预估')} style={{ marginTop: 16 }}>
        <Row gutter={[16, 16]}>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: '#1890ff' }}>
                {estimatedSize.toFixed(1)} MB
              </div>
              <div style={{ color: '#666' }}>{t('export.estimate.size', '预估文件大小')}</div>
            </div>
          </Col>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: '#52c41a' }}>
                {Math.floor(estimatedTime / 60)}:{(estimatedTime % 60).toFixed(0).padStart(2, '0')}
              </div>
              <div style={{ color: '#666' }}>{t('export.estimate.time', '预估导出时间')}</div>
            </div>
          </Col>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: '#fa8c16' }}>
                {exportConfig.resolution}
              </div>
              <div style={{ color: '#666' }}>{t('export.estimate.resolution', '输出分辨率')}</div>
            </div>
          </Col>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: '#eb2f96' }}>
                {exportConfig.format.toUpperCase()}
              </div>
              <div style={{ color: '#666' }}>{t('export.estimate.format', '输出格式')}</div>
            </div>
          </Col>
        </Row>
      </Card>

      {/* 导出按钮 */}
      <div style={{ textAlign: 'center', marginTop: 24 }}>
        <Space size="large">
          <Button onClick={resetToDefaults}>
            {t('export.reset.btn', '重置设置')}
          </Button>
          
          <Button
            type="primary"
            size="large"
            icon={<DownloadOutlined />}
            onClick={handleExport}
            loading={isExporting}
            disabled={isExporting}
          >
            {isExporting ? t('export.processing', '导出中...') : t('export.start', '开始导出')}
          </Button>
        </Space>
      </div>

      {/* 导出进度 */}
      {isExporting && (
        <Card style={{ marginTop: 16 }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ marginBottom: 16 }}>
              <CloudDownloadOutlined style={{ fontSize: 32, color: '#1890ff' }} />
            </div>
            <Progress 
              percent={Math.floor(exportProgress)} 
              status={exportProgress >= 100 ? 'success' : 'active'}
              strokeWidth={8}
            />
            <div style={{ marginTop: 8, color: '#666' }}>
              正在导出视频，请稍候...
            </div>
          </div>
        </Card>
      )}

      {/* 提示信息 */}
      <Alert
        message={t('export.tip.title', '导出提示')}
        description={
          <div>
            <p>• {t('export.tip.resolution', '高分辨率和高码率会显著增加文件大小和导出时间')}</p>
            <p>• {t('export.tip.hwaccel', '启用硬件加速可以大幅提升导出速度')}</p>
            <p>• {t('export.tip.twopass', '两遍编码会提高质量但增加导出时间')}</p>
            <p>• {t('export.tip.h265', 'H.265编码文件更小但兼容性稍差')}</p>
          </div>
        }
        type="info"
        showIcon
        style={{ marginTop: 16 }}
      />
    </div>
  );
}

export default ExportSettings;