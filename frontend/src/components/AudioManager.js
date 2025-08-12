import React, { useState, useEffect, useRef } from 'react';
import { 
  Card, 
  Upload, 
  Button, 
  List, 
  Slider, 
  Switch, 
  Select, 
  Row, 
  Col, 
  message,
  Popconfirm,
  Progress,
  Tag
} from 'antd';
import { 
  UploadOutlined, 
  PlayCircleOutlined, 
  PauseCircleOutlined,
  DeleteOutlined,
  SoundOutlined,
  MutedOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Option } = Select;

function AudioManager({ onAudioConfigChange }) {
  const [audioFiles, setAudioFiles] = useState([]);
  const [backgroundMusic, setBackgroundMusic] = useState(null);
  const [soundEffects, setSoundEffects] = useState([]);
  const [musicVolume, setMusicVolume] = useState(50);
  const [effectsVolume, setEffectsVolume] = useState(70);
  const [fadeInOut, setFadeInOut] = useState(true);
  const [currentPlaying, setCurrentPlaying] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const audioRef = useRef(null);

  // 预设音效类型
  const effectTypes = [
    { value: 'transition', label: '转场音效', color: 'blue' },
    { value: 'emphasis', label: '强调音效', color: 'orange' },
    { value: 'ambient', label: '环境音效', color: 'green' },
    { value: 'notification', label: '提示音效', color: 'purple' }
  ];

  useEffect(() => {
    loadAudioFiles();
  }, []);

  useEffect(() => {
    // 通知父组件音频配置变化
    const audioConfig = {
      backgroundMusic: backgroundMusic ? {
        file: backgroundMusic,
        volume: musicVolume / 100,
        fadeInOut
      } : null,
      soundEffects: soundEffects.map(effect => ({
        ...effect,
        volume: effectsVolume / 100
      }))
    };
    
    onAudioConfigChange && onAudioConfigChange(audioConfig);
  }, [backgroundMusic, soundEffects, musicVolume, effectsVolume, fadeInOut]);

  const loadAudioFiles = async () => {
    try {
      const response = await axios.get('/api/user-assets/list', {
        params: { type: 'audio' }
      });
      setAudioFiles(response.data.assets || []);
    } catch (error) {
      console.error('加载音频文件失败:', error);
    }
  };

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', 'audio');
    formData.append('category', 'music');

    try {
      setUploadProgress(0);
      const response = await axios.post('/api/user-assets/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(progress);
        }
      });

      message.success('音频文件上传成功');
      loadAudioFiles();
      setUploadProgress(0);
    } catch (error) {
      console.error('上传失败:', error);
      message.error('音频文件上传失败');
      setUploadProgress(0);
    }

    return false; // 阻止默认上传行为
  };

  const playAudio = (audioFile) => {
    if (currentPlaying === audioFile.id) {
      // 暂停当前播放
      if (audioRef.current) {
        audioRef.current.pause();
        setCurrentPlaying(null);
      }
    } else {
      // 播放新音频
      if (audioRef.current) {
        audioRef.current.src = audioFile.url;
        audioRef.current.play();
        setCurrentPlaying(audioFile.id);
      }
    }
  };

  const handleAudioEnded = () => {
    setCurrentPlaying(null);
  };

  const setAsBackgroundMusic = (audioFile) => {
    setBackgroundMusic(audioFile);
    message.success(`已设置 "${audioFile.name}" 为背景音乐`);
  };

  const addSoundEffect = (audioFile, sceneIndex, timing, effectType) => {
    const newEffect = {
      id: Date.now(),
      audioFile,
      sceneIndex,
      timing, // 在场景中的时间点（秒）
      type: effectType,
      volume: effectsVolume / 100
    };

    setSoundEffects(prev => [...prev, newEffect]);
    message.success(`已添加音效到场景 ${sceneIndex + 1}`);
  };

  const removeSoundEffect = (effectId) => {
    setSoundEffects(prev => prev.filter(effect => effect.id !== effectId));
    message.success('已移除音效');
  };

  const deleteAudioFile = async (audioId) => {
    try {
      await axios.delete(`/api/user-assets/${audioId}`);
      message.success('音频文件已删除');
      loadAudioFiles();
      
      // 如果删除的是当前背景音乐，清除设置
      if (backgroundMusic && backgroundMusic.id === audioId) {
        setBackgroundMusic(null);
      }
      
      // 移除相关的音效
      setSoundEffects(prev => 
        prev.filter(effect => effect.audioFile.id !== audioId)
      );
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除音频文件失败');
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="audio-manager">
      <audio 
        ref={audioRef} 
        onEnded={handleAudioEnded}
        style={{ display: 'none' }}
      />

      <Row gutter={[16, 16]}>
        {/* 音频文件库 */}
        <Col span={12}>
          <Card 
            title="音频文件库" 
            extra={
              <Upload
                beforeUpload={handleUpload}
                accept="audio/*"
                showUploadList={false}
              >
                <Button icon={<UploadOutlined />} size="small">
                  上传音频
                </Button>
              </Upload>
            }
          >
            {uploadProgress > 0 && (
              <Progress 
                percent={uploadProgress} 
                size="small" 
                style={{ marginBottom: 16 }}
              />
            )}
            
            <List
              size="small"
              dataSource={audioFiles}
              renderItem={(audio) => (
                <List.Item
                  actions={[
                    <Button
                      type="text"
                      size="small"
                      icon={
                        currentPlaying === audio.id ? 
                        <PauseCircleOutlined /> : 
                        <PlayCircleOutlined />
                      }
                      onClick={() => playAudio(audio)}
                    />,
                    <Button
                      type="text"
                      size="small"
                      onClick={() => setAsBackgroundMusic(audio)}
                    >
                      设为背景音乐
                    </Button>,
                    <Popconfirm
                      title="确定删除这个音频文件吗？"
                      onConfirm={() => deleteAudioFile(audio.id)}
                    >
                      <Button
                        type="text"
                        size="small"
                        danger
                        icon={<DeleteOutlined />}
                      />
                    </Popconfirm>
                  ]}
                >
                  <List.Item.Meta
                    title={audio.name}
                    description={
                      <div>
                        <span>大小: {(audio.size / 1024 / 1024).toFixed(2)}MB</span>
                        {audio.duration && (
                          <span style={{ marginLeft: 8 }}>
                            时长: {formatDuration(audio.duration)}
                          </span>
                        )}
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 音频设置 */}
        <Col span={12}>
          <Card title="音频设置">
            {/* 背景音乐设置 */}
            <div style={{ marginBottom: 24 }}>
              <h4>
                <SoundOutlined /> 背景音乐
              </h4>
              {backgroundMusic ? (
                <div>
                  <p><strong>{backgroundMusic.name}</strong></p>
                  <div style={{ marginBottom: 8 }}>
                    <span>音量: </span>
                    <Slider
                      value={musicVolume}
                      onChange={setMusicVolume}
                      style={{ width: 120, display: 'inline-block', marginLeft: 8 }}
                    />
                    <span style={{ marginLeft: 8 }}>{musicVolume}%</span>
                  </div>
                  <div>
                    <Switch
                      checked={fadeInOut}
                      onChange={setFadeInOut}
                      size="small"
                    />
                    <span style={{ marginLeft: 8 }}>淡入淡出</span>
                  </div>
                  <Button
                    type="link"
                    size="small"
                    onClick={() => setBackgroundMusic(null)}
                  >
                    移除背景音乐
                  </Button>
                </div>
              ) : (
                <p style={{ color: '#999' }}>未设置背景音乐</p>
              )}
            </div>

            {/* 音效设置 */}
            <div>
              <h4>
                <MutedOutlined /> 音效设置
              </h4>
              <div style={{ marginBottom: 16 }}>
                <span>音效音量: </span>
                <Slider
                  value={effectsVolume}
                  onChange={setEffectsVolume}
                  style={{ width: 120, display: 'inline-block', marginLeft: 8 }}
                />
                <span style={{ marginLeft: 8 }}>{effectsVolume}%</span>
              </div>

              {soundEffects.length > 0 ? (
                <List
                  size="small"
                  dataSource={soundEffects}
                  renderItem={(effect) => (
                    <List.Item
                      actions={[
                        <Button
                          type="text"
                          size="small"
                          danger
                          icon={<DeleteOutlined />}
                          onClick={() => removeSoundEffect(effect.id)}
                        />
                      ]}
                    >
                      <List.Item.Meta
                        title={
                          <div>
                            {effect.audioFile.name}
                            <Tag 
                              color={effectTypes.find(t => t.value === effect.type)?.color}
                              size="small"
                              style={{ marginLeft: 8 }}
                            >
                              {effectTypes.find(t => t.value === effect.type)?.label}
                            </Tag>
                          </div>
                        }
                        description={`场景 ${effect.sceneIndex + 1} - ${effect.timing}秒`}
                      />
                    </List.Item>
                  )}
                />
              ) : (
                <p style={{ color: '#999' }}>暂无音效</p>
              )}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 快速添加音效面板 */}
      {audioFiles.length > 0 && (
        <Card title="快速添加音效" style={{ marginTop: 16 }}>
          <Row gutter={[8, 8]}>
            <Col span={6}>
              <Select placeholder="选择音频" style={{ width: '100%' }}>
                {audioFiles.map(audio => (
                  <Option key={audio.id} value={audio.id}>
                    {audio.name}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col span={4}>
              <Select placeholder="场景" style={{ width: '100%' }}>
                <Option value={0}>场景 1</Option>
                <Option value={1}>场景 2</Option>
                <Option value={2}>场景 3</Option>
              </Select>
            </Col>
            <Col span={4}>
              <Select placeholder="时间点" style={{ width: '100%' }}>
                <Option value={0}>开始</Option>
                <Option value={2}>2秒</Option>
                <Option value={5}>5秒</Option>
              </Select>
            </Col>
            <Col span={6}>
              <Select placeholder="音效类型" style={{ width: '100%' }}>
                {effectTypes.map(type => (
                  <Option key={type.value} value={type.value}>
                    {type.label}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col span={4}>
              <Button type="primary" size="small">
                添加音效
              </Button>
            </Col>
          </Row>
        </Card>
      )}
    </div>
  );
}

export default AudioManager;