import React, { useState, useEffect } from 'react';
import { Card, Select, Switch, Slider, Button, Row, Col, Divider, Alert } from 'antd';
import { SoundOutlined, PlayCircleOutlined } from '@ant-design/icons';
import api from '../utils/api';
import { t } from '../utils/i18n';

const { Option } = Select;

function VoiceSelector({ voiceConfig, onVoiceConfigChange }) {
  const [voices, setVoices] = useState({ gtts: [], openai: [] });
  const [loading, setLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    fetchVoices();
  }, []);

  const fetchVoices = async () => {
    try {
      const data = await api.get('/video/voices');
      setVoices(data.voices || { gtts: [], openai: [] });
    } catch (error) {
      console.error('获取语音选项失败:', error);
    }
  };

  const handleConfigChange = (key, value) => {
    const newConfig = { ...voiceConfig, [key]: value };
    onVoiceConfigChange(newConfig);
  };

  const handlePreviewVoice = async () => {
    setLoading(true);
    try {
      const data = await api.post('/video/preview-voice', {
        text: t('voice.preview.sample', '这是一个语音预览示例，您可以听到选择的语音效果。'),
        voice_config: voiceConfig
      });
      
      setPreviewUrl(data.audio_url);
      
      // 播放音频
      const audio = new Audio(data.audio_url);
      audio.play();
      
    } catch (error) {
      console.error('语音预览失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentVoices = () => {
    return voices[voiceConfig.provider] || [];
  };

  const getVoiceName = (voiceId) => {
    const currentVoices = getCurrentVoices();
    const voice = currentVoices.find(v => v.id === voiceId);
    return voice ? voice.name : voiceId;
  };

  return (
    <Card title={t('voice.title', '语音配置')} size="small">
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span><strong>{t('voice.enable', '启用语音：')}</strong></span>
            <Switch 
              checked={voiceConfig.enabled}
              onChange={(checked) => handleConfigChange('enabled', checked)}
              checkedChildren={t('common.on', '开启')}
              unCheckedChildren={t('common.off', '关闭')}
            />
          </div>
        </Col>

        {voiceConfig.enabled && (
          <>
            <Col span={24}>
              <Divider style={{ margin: '12px 0' }} />
            </Col>

            <Col span={12}>
              <div>
                <label><strong>{t('voice.provider', '语音服务：')}</strong></label>
                <Select
                  value={voiceConfig.provider}
                  onChange={(value) => handleConfigChange('provider', value)}
                  style={{ width: '100%', marginTop: 8 }}
                >
                  <Option value="gtts">{t('voice.provider.gtts', 'Google TTS（免费）')}</Option>
                  <Option value="openai">{t('voice.provider.openai', 'OpenAI TTS（需要 API 密钥）')}</Option>
                </Select>
              </div>
            </Col>

            <Col span={12}>
              <div>
                <label><strong>{t('voice.select', '语音选择：')}</strong></label>
                <Select
                  value={voiceConfig.voice}
                  onChange={(value) => handleConfigChange('voice', value)}
                  style={{ width: '100%', marginTop: 8 }}
                  placeholder={t('voice.select.placeholder', '选择语音')}
                >
                  {getCurrentVoices().map(voice => (
                    <Option key={voice.id} value={voice.id}>
                      <div>
                        <div style={{ fontWeight: 'bold' }}>{voice.name}</div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          {voice.language}
                        </div>
                      </div>
                    </Option>
                  ))}
                </Select>
              </div>
            </Col>

            <Col span={24}>
              <div>
                <label><strong>{t('voice.speed', '语速：')}</strong></label>
                <Slider
                  min={0.5}
                  max={2.0}
                  step={0.1}
                  value={voiceConfig.speed}
                  onChange={(value) => handleConfigChange('speed', value)}
                  marks={{
                    0.5: '0.5x',
                    1.0: '1.0x',
                    1.5: '1.5x',
                    2.0: '2.0x'
                  }}
                  style={{ marginTop: 8 }}
                />
              </div>
            </Col>

            <Col span={24}>
              <div style={{ textAlign: 'center' }}>
                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  onClick={handlePreviewVoice}
                  loading={loading}
                  size="small"
                >
                  {t('voice.preview', '预览语音效果')}
                </Button>
              </div>
            </Col>

            {voiceConfig.provider === 'openai' && (
              <Col span={24}>
                <Alert
                  message={t('voice.openai.title', 'OpenAI TTS 说明')}
                  description={t('voice.openai.desc', '使用 OpenAI TTS 需要配置 API 密钥，语音质量更高，支持多种语言和语音风格。')}
                  type="info"
                  showIcon
                  style={{ fontSize: '12px' }}
                />
              </Col>
            )}
          </>
        )}
      </Row>

      <div style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
        <div style={{ fontSize: '12px', color: '#666' }}>
          <SoundOutlined style={{ marginRight: 4 }} />
          当前配置：
          {voiceConfig.enabled ? (
            <>
              {voiceConfig.provider === 'gtts' ? 'Google TTS' : 'OpenAI TTS'} - 
              {getVoiceName(voiceConfig.voice)} - 
              {voiceConfig.speed}x 语速
            </>
          ) : (
            '语音已关闭'
          )}
        </div>
      </div>
    </Card>
  );
}

export default VoiceSelector;