import React, { useState, useRef, useEffect } from 'react';
import { Card, Slider, Button, Space, Tooltip } from 'antd';
import { PlayCircleOutlined, PauseOutlined, StepBackwardOutlined, StepForwardOutlined } from '@ant-design/icons';

function VideoTimeline({ script, onSceneChange, currentScene = 0 }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [totalDuration, setTotalDuration] = useState(0);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (script && script.scenes) {
      const total = script.scenes.reduce((sum, scene) => sum + scene.duration, 0);
      setTotalDuration(total);
    }
  }, [script]);

  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        setCurrentTime(prev => {
          const newTime = prev + 0.1;
          if (newTime >= totalDuration) {
            setIsPlaying(false);
            return 0;
          }
          
          // 计算当前应该在哪个场景
          let accumulatedTime = 0;
          let sceneIndex = 0;
          for (let i = 0; i < script.scenes.length; i++) {
            if (newTime >= accumulatedTime && newTime < accumulatedTime + script.scenes[i].duration) {
              sceneIndex = i;
              break;
            }
            accumulatedTime += script.scenes[i].duration;
          }
          
          if (sceneIndex !== currentScene) {
            onSceneChange(sceneIndex);
          }
          
          return newTime;
        });
      }, 100);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, totalDuration, currentScene, onSceneChange, script]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleTimeChange = (value) => {
    setCurrentTime(value);
    
    // 计算对应的场景
    let accumulatedTime = 0;
    let sceneIndex = 0;
    for (let i = 0; i < script.scenes.length; i++) {
      if (value >= accumulatedTime && value < accumulatedTime + script.scenes[i].duration) {
        sceneIndex = i;
        break;
      }
      accumulatedTime += script.scenes[i].duration;
    }
    
    onSceneChange(sceneIndex);
  };

  const handlePrevScene = () => {
    const newScene = Math.max(0, currentScene - 1);
    onSceneChange(newScene);
    
    // 计算新场景的开始时间
    let startTime = 0;
    for (let i = 0; i < newScene; i++) {
      startTime += script.scenes[i].duration;
    }
    setCurrentTime(startTime);
  };

  const handleNextScene = () => {
    const newScene = Math.min(script.scenes.length - 1, currentScene + 1);
    onSceneChange(newScene);
    
    // 计算新场景的开始时间
    let startTime = 0;
    for (let i = 0; i < newScene; i++) {
      startTime += script.scenes[i].duration;
    }
    setCurrentTime(startTime);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSceneMarkers = () => {
    if (!script || !script.scenes) return [];
    
    let accumulatedTime = 0;
    return script.scenes.map((scene, index) => {
      const startTime = accumulatedTime;
      accumulatedTime += scene.duration;
      return {
        index,
        startTime,
        endTime: accumulatedTime,
        duration: scene.duration,
        text: scene.text
      };
    });
  };

  if (!script || !script.scenes) {
    return null;
  }

  const sceneMarkers = getSceneMarkers();

  return (
    <Card title="视频时间轴" size="small">
      <div style={{ padding: '16px 0' }}>
        {/* 播放控制 */}
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
          <Space>
            <Tooltip title="上一场景">
              <Button 
                icon={<StepBackwardOutlined />} 
                onClick={handlePrevScene}
                disabled={currentScene === 0}
              />
            </Tooltip>
            
            <Tooltip title={isPlaying ? "暂停" : "播放"}>
              <Button 
                type="primary"
                icon={isPlaying ? <PauseOutlined /> : <PlayCircleOutlined />}
                onClick={handlePlayPause}
              />
            </Tooltip>
            
            <Tooltip title="下一场景">
              <Button 
                icon={<StepForwardOutlined />} 
                onClick={handleNextScene}
                disabled={currentScene === script.scenes.length - 1}
              />
            </Tooltip>
          </Space>
          
          <div style={{ marginLeft: 16, fontSize: '14px', color: '#666' }}>
            {formatTime(currentTime)} / {formatTime(totalDuration)}
          </div>
        </div>

        {/* 时间轴滑块 */}
        <div style={{ position: 'relative', marginBottom: 16 }}>
          <Slider
            min={0}
            max={totalDuration}
            step={0.1}
            value={currentTime}
            onChange={handleTimeChange}
            tooltip={{
              formatter: (value) => formatTime(value)
            }}
          />
          
          {/* 场景标记 */}
          <div style={{ position: 'relative', height: '20px', marginTop: '8px' }}>
            {sceneMarkers.map((marker, index) => (
              <div
                key={index}
                style={{
                  position: 'absolute',
                  left: `${(marker.startTime / totalDuration) * 100}%`,
                  width: `${(marker.duration / totalDuration) * 100}%`,
                  height: '16px',
                  background: index === currentScene ? '#1890ff' : '#f0f0f0',
                  border: '1px solid #d9d9d9',
                  borderRadius: '2px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '10px',
                  color: index === currentScene ? 'white' : '#666'
                }}
                onClick={() => {
                  onSceneChange(index);
                  setCurrentTime(marker.startTime);
                }}
              >
                {index + 1}
              </div>
            ))}
          </div>
        </div>

        {/* 当前场景信息 */}
        <div style={{ 
          background: '#f5f5f5', 
          padding: '12px', 
          borderRadius: '4px',
          fontSize: '14px'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
            场景 {currentScene + 1} / {script.scenes.length}
          </div>
          <div style={{ color: '#666' }}>
            {script.scenes[currentScene]?.text}
          </div>
          <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
            时长: {script.scenes[currentScene]?.duration}秒
          </div>
        </div>
      </div>
    </Card>
  );
}

export default VideoTimeline;