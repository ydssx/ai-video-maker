import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, Slider, Button, Space, Tooltip, Dropdown, Menu, Progress, Tag } from 'antd';
import { 
  PlayCircleOutlined, 
  PauseOutlined, 
  StepBackwardOutlined, 
  StepForwardOutlined,
  FastBackwardOutlined,
  FastForwardOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { t } from '../utils/i18n';

function VideoTimeline({ script, onSceneChange, currentScene = 0 }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [totalDuration, setTotalDuration] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const rafRef = useRef(null);
  const lastTickRef = useRef(null);
  const sliderRef = useRef(null);

  // 格式化时间显示
  const formatTime = useCallback((seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, []);

  // 获取场景信息
  const getSceneInfo = useCallback(() => {
    if (!script || !script.scenes) return [];
    
    return script.scenes.map((scene, index) => {
      let startTime = 0;
      for (let i = 0; i < index; i++) {
        startTime += script.scenes[i].duration;
      }
      
      return {
        ...scene,
        index,
        startTime,
        endTime: startTime + scene.duration
      };
    });
  }, [script]);

  // 计算当前场景
  const getCurrentSceneIndex = useCallback((time) => {
    const scenes = getSceneInfo();
    for (let i = 0; i < scenes.length; i++) {
      if (time >= scenes[i].startTime && time < scenes[i].endTime) {
        return i;
      }
    }
    return 0;
  }, [getSceneInfo]);

  useEffect(() => {
    if (script && script.scenes) {
      const total = script.scenes.reduce((sum, scene) => sum + scene.duration, 0);
      setTotalDuration(total);
    }
  }, [script]);

  // 使用requestAnimationFrame优化播放控制
  useEffect(() => {
    const tick = (now) => {
      if (!lastTickRef.current) lastTickRef.current = now;
      const deltaMs = now - lastTickRef.current;
      lastTickRef.current = now;
      
      setCurrentTime(prev => {
        const newTime = prev + deltaMs / 1000;
        if (newTime >= totalDuration) {
          setIsPlaying(false);
          return 0;
        }
        
        // 检查场景变化
        const newSceneIndex = getCurrentSceneIndex(newTime);
        if (newSceneIndex !== currentScene) {
          onSceneChange(newSceneIndex);
        }
        
        return newTime;
      });
      
      rafRef.current = requestAnimationFrame(tick);
    };

    if (isPlaying && !isDragging) {
      rafRef.current = requestAnimationFrame(tick);
    } else {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      lastTickRef.current = null;
    }

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [isPlaying, totalDuration, currentScene, onSceneChange, getCurrentSceneIndex, isDragging]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleTimeChange = useCallback((value) => {
    setCurrentTime(value);
    
    if (!isDragging) {
      const newSceneIndex = getCurrentSceneIndex(value);
      onSceneChange(newSceneIndex);
    }
  }, [isDragging, getCurrentSceneIndex, onSceneChange]);

  const handleSliderChange = useCallback((value) => {
    setCurrentTime(value);
  }, []);

  const handleSliderAfterChange = useCallback((value) => {
    setIsDragging(false);
    const newSceneIndex = getCurrentSceneIndex(value);
    onSceneChange(newSceneIndex);
  }, [getCurrentSceneIndex, onSceneChange]);

  const handleSliderBeforeChange = useCallback(() => {
    setIsDragging(true);
  }, []);

  const handlePrevScene = useCallback(() => {
    const newScene = Math.max(0, currentScene - 1);
    onSceneChange(newScene);
    
    const scenes = getSceneInfo();
    if (scenes[newScene]) {
      setCurrentTime(scenes[newScene].startTime);
    }
  }, [currentScene, onSceneChange, getSceneInfo]);

  const handleNextScene = useCallback(() => {
    const newScene = Math.min(script.scenes.length - 1, currentScene + 1);
    onSceneChange(newScene);
    
    const scenes = getSceneInfo();
    if (scenes[newScene]) {
      setCurrentTime(scenes[newScene].startTime);
    }
  }, [currentScene, onSceneChange, script.scenes.length, getSceneInfo]);

  const handleJumpToStart = useCallback(() => {
    setCurrentTime(0);
    onSceneChange(0);
  }, [onSceneChange]);

  const handleJumpToEnd = useCallback(() => {
    setCurrentTime(totalDuration);
    onSceneChange(script.scenes.length - 1);
  }, [totalDuration, script.scenes.length, onSceneChange]);

  // 场景跳转菜单
  const sceneMenu = (
    <Menu>
      {getSceneInfo().map((scene, index) => (
        <Menu.Item 
          key={index}
          onClick={() => {
            onSceneChange(index);
            setCurrentTime(scene.startTime);
          }}
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
        >
          <span>场景 {index + 1}</span>
          <Tag size="small">{formatTime(scene.duration)}</Tag>
        </Menu.Item>
      ))}
    </Menu>
  );

  if (!script || !script.scenes) {
    return (
      <Card title="视频时间轴" size="small">
        <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
          暂无脚本内容
        </div>
      </Card>
    );
  }

  const scenes = getSceneInfo();
  const currentSceneInfo = scenes[currentScene] || scenes[0];

  return (
    <Card title="视频时间轴" size="small">
      {/* 播放控制 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Button 
            type="primary" 
            icon={isPlaying ? <PauseOutlined /> : <PlayCircleOutlined />}
            onClick={handlePlayPause}
            aria-label={isPlaying ? '暂停' : '播放'}
          >
            {isPlaying ? '暂停' : '播放'}
          </Button>
          
          <Button 
            icon={<StepBackwardOutlined />} 
            onClick={handlePrevScene}
            disabled={currentScene === 0}
            aria-label="上一个场景"
          />
          
          <Button 
            icon={<StepForwardOutlined />} 
            onClick={handleNextScene}
            disabled={currentScene === script.scenes.length - 1}
            aria-label="下一个场景"
          />
          
          <Button 
            icon={<FastBackwardOutlined />} 
            onClick={handleJumpToStart}
            aria-label="跳转到开始"
          />
          
          <Button 
            icon={<FastForwardOutlined />} 
            onClick={handleJumpToEnd}
            aria-label="跳转到结束"
          />
          
          <Dropdown overlay={sceneMenu} placement="bottomCenter">
            <Button>
              场景 {currentScene + 1} / {script.scenes.length}
            </Button>
          </Dropdown>
        </Space>
      </div>

      {/* 时间轴滑块 */}
      <div style={{ marginBottom: 16 }}>
        <Slider
          ref={sliderRef}
          min={0}
          max={totalDuration}
          value={currentTime}
          onChange={handleSliderChange}
          onAfterChange={handleSliderAfterChange}
          onBeforeChange={handleSliderBeforeChange}
          step={0.1}
          tooltip={{
            formatter: formatTime
          }}
          style={{ margin: '0 8px' }}
        />
        
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          fontSize: '12px', 
          color: '#666',
          marginTop: '8px'
        }}>
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(totalDuration)}</span>
        </div>
      </div>

      {/* 当前场景信息 */}
      {currentSceneInfo && (
        <div style={{ 
          background: '#f5f5f5', 
          padding: '12px', 
          borderRadius: '6px',
          marginBottom: '16px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <strong>当前场景: {currentScene + 1}</strong>
            <Tag icon={<ClockCircleOutlined />} color="blue">
              {formatTime(currentSceneInfo.duration)}
            </Tag>
          </div>
          
          <Tooltip title={currentSceneInfo.content || '无内容描述'}>
            <p style={{ 
              margin: 0, 
              color: '#666', 
              fontSize: '14px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}>
              {currentSceneInfo.content || '无内容描述'}
            </p>
          </Tooltip>
        </div>
      )}

      {/* 场景进度条 */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: '8px', fontSize: '12px', color: '#666' }}>
          场景进度
        </div>
        <Progress
          percent={((currentScene + 1) / script.scenes.length) * 100}
          size="small"
          showInfo={false}
        />
      </div>

      {/* 场景列表 */}
      <div>
        <div style={{ marginBottom: '8px', fontSize: '12px', color: '#666' }}>
          场景列表
        </div>
        <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
          {scenes.map((scene, index) => (
            <div
              key={index}
              style={{
                padding: '8px 12px',
                margin: '4px 0',
                background: index === currentScene ? '#e6f7ff' : '#fafafa',
                border: index === currentScene ? '1px solid #91d5ff' : '1px solid #f0f0f0',
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
              onClick={() => {
                onSceneChange(index);
                setCurrentTime(scene.startTime);
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSceneChange(index);
                  setCurrentTime(scene.startTime);
                }
              }}
              tabIndex={0}
              role="button"
              aria-label={`跳转到场景 ${index + 1}`}
            >
              <span>场景 {index + 1}</span>
              <Tag size="small">{formatTime(scene.duration)}</Tag>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

export default VideoTimeline;