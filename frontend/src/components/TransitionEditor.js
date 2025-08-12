import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Select, 
  Slider, 
  Row, 
  Col, 
  Button, 
  List, 
  Tag, 
  Divider,
  Tooltip,
  Space,
  message
} from 'antd';
import { 
  PlayCircleOutlined, 
  SettingOutlined,
  SwapOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';

const { Option } = Select;

function TransitionEditor({ script, onTransitionChange }) {
  const [transitions, setTransitions] = useState([]);
  const [selectedTransition, setSelectedTransition] = useState(null);
  const [previewMode, setPreviewMode] = useState(false);

  // 转场效果类型
  const transitionTypes = [
    {
      id: 'fade',
      name: '淡入淡出',
      description: '平滑的透明度过渡',
      duration: [0.5, 3],
      color: 'blue',
      preview: '●○●'
    },
    {
      id: 'slide_left',
      name: '左滑',
      description: '从右向左滑动',
      duration: [0.3, 2],
      color: 'green',
      preview: '→←'
    },
    {
      id: 'slide_right',
      name: '右滑',
      description: '从左向右滑动',
      duration: [0.3, 2],
      color: 'green',
      preview: '←→'
    },
    {
      id: 'slide_up',
      name: '上滑',
      description: '从下向上滑动',
      duration: [0.3, 2],
      color: 'green',
      preview: '↑'
    },
    {
      id: 'slide_down',
      name: '下滑',
      description: '从上向下滑动',
      duration: [0.3, 2],
      color: 'green',
      preview: '↓'
    },
    {
      id: 'zoom_in',
      name: '放大',
      description: '缩放放大效果',
      duration: [0.5, 2],
      color: 'orange',
      preview: '⊙'
    },
    {
      id: 'zoom_out',
      name: '缩小',
      description: '缩放缩小效果',
      duration: [0.5, 2],
      color: 'orange',
      preview: '○'
    },
    {
      id: 'rotate',
      name: '旋转',
      description: '旋转过渡效果',
      duration: [0.8, 3],
      color: 'purple',
      preview: '↻'
    },
    {
      id: 'flip_horizontal',
      name: '水平翻转',
      description: '水平翻转过渡',
      duration: [0.6, 2],
      color: 'cyan',
      preview: '⟷'
    },
    {
      id: 'flip_vertical',
      name: '垂直翻转',
      description: '垂直翻转过渡',
      duration: [0.6, 2],
      color: 'cyan',
      preview: '↕'
    },
    {
      id: 'dissolve',
      name: '溶解',
      description: '像素溶解效果',
      duration: [1, 3],
      color: 'magenta',
      preview: '⋯'
    },
    {
      id: 'wipe_left',
      name: '左擦除',
      description: '从左到右擦除',
      duration: [0.5, 2],
      color: 'red',
      preview: '▌'
    },
    {
      id: 'wipe_right',
      name: '右擦除',
      description: '从右到左擦除',
      duration: [0.5, 2],
      color: 'red',
      preview: '▐'
    },
    {
      id: 'circle_in',
      name: '圆形收缩',
      description: '圆形收缩过渡',
      duration: [0.8, 2.5],
      color: 'gold',
      preview: '◉'
    },
    {
      id: 'circle_out',
      name: '圆形扩展',
      description: '圆形扩展过渡',
      duration: [0.8, 2.5],
      color: 'gold',
      preview: '○'
    }
  ];

  useEffect(() => {
    // 初始化转场设置
    if (script && script.scenes) {
      const initialTransitions = script.scenes.slice(0, -1).map((scene, index) => ({
        id: `transition_${index}`,
        fromScene: index,
        toScene: index + 1,
        type: 'fade',
        duration: 1.0,
        easing: 'ease-in-out',
        customSettings: {}
      }));
      setTransitions(initialTransitions);
    }
  }, [script]);

  useEffect(() => {
    // 通知父组件转场配置变化
    onTransitionChange && onTransitionChange(transitions);
  }, [transitions]);

  const updateTransition = (transitionId, updates) => {
    setTransitions(prev => 
      prev.map(transition => 
        transition.id === transitionId 
          ? { ...transition, ...updates }
          : transition
      )
    );
  };

  const getTransitionType = (typeId) => {
    return transitionTypes.find(type => type.id === typeId);
  };

  const applyToAll = (property, value) => {
    setTransitions(prev => 
      prev.map(transition => ({
        ...transition,
        [property]: value
      }))
    );
    message.success(`已将${property === 'type' ? '转场类型' : '持续时间'}应用到所有转场`);
  };

  const resetTransitions = () => {
    const defaultTransitions = script.scenes.slice(0, -1).map((scene, index) => ({
      id: `transition_${index}`,
      fromScene: index,
      toScene: index + 1,
      type: 'fade',
      duration: 1.0,
      easing: 'ease-in-out',
      customSettings: {}
    }));
    setTransitions(defaultTransitions);
    message.success('已重置所有转场效果');
  };

  const previewTransition = (transition) => {
    setSelectedTransition(transition);
    setPreviewMode(true);
    // 这里可以添加预览逻辑
    message.info(`预览转场: ${getTransitionType(transition.type)?.name}`);
    
    // 模拟预览结束
    setTimeout(() => {
      setPreviewMode(false);
    }, 2000);
  };

  if (!script || !script.scenes || script.scenes.length < 2) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
          <SwapOutlined style={{ fontSize: 48, marginBottom: 16 }} />
          <p>需要至少2个场景才能设置转场效果</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="transition-editor">
      <Row gutter={[16, 16]}>
        {/* 转场效果库 */}
        <Col span={8}>
          <Card title="转场效果库" size="small">
            <List
              size="small"
              dataSource={transitionTypes}
              renderItem={(type) => (
                <List.Item
                  style={{ 
                    cursor: 'pointer',
                    padding: '8px 12px',
                    borderRadius: 4,
                    marginBottom: 4,
                    backgroundColor: selectedTransition?.type === type.id ? '#f0f0f0' : 'transparent'
                  }}
                  onClick={() => {
                    if (selectedTransition) {
                      updateTransition(selectedTransition.id, { type: type.id });
                    }
                  }}
                >
                  <List.Item.Meta
                    avatar={
                      <div style={{ 
                        width: 32, 
                        height: 32, 
                        borderRadius: 4,
                        backgroundColor: `var(--ant-color-${type.color})`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: 14,
                        fontWeight: 'bold'
                      }}>
                        {type.preview}
                      </div>
                    }
                    title={type.name}
                    description={
                      <div>
                        <div style={{ fontSize: 12, color: '#666' }}>
                          {type.description}
                        </div>
                        <div style={{ fontSize: 11, color: '#999', marginTop: 2 }}>
                          时长: {type.duration[0]}s - {type.duration[1]}s
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 转场列表 */}
        <Col span={16}>
          <Card 
            title="场景转场设置"
            extra={
              <Space>
                <Button size="small" onClick={resetTransitions}>
                  重置全部
                </Button>
                <Button 
                  size="small" 
                  type="primary"
                  onClick={() => setPreviewMode(!previewMode)}
                  loading={previewMode}
                >
                  {previewMode ? '预览中...' : '预览全部'}
                </Button>
              </Space>
            }
          >
            <List
              dataSource={transitions}
              renderItem={(transition, index) => {
                const transitionType = getTransitionType(transition.type);
                return (
                  <List.Item
                    style={{
                      backgroundColor: selectedTransition?.id === transition.id ? '#f6ffed' : 'transparent',
                      border: selectedTransition?.id === transition.id ? '1px solid #b7eb8f' : '1px solid transparent',
                      borderRadius: 6,
                      marginBottom: 8,
                      padding: 16
                    }}
                    onClick={() => setSelectedTransition(transition)}
                  >
                    <Row style={{ width: '100%' }} gutter={[16, 8]}>
                      <Col span={6}>
                        <div>
                          <strong>场景 {transition.fromScene + 1} → 场景 {transition.toScene + 1}</strong>
                          <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
                            {script.scenes[transition.fromScene]?.text?.substring(0, 30)}...
                          </div>
                        </div>
                      </Col>
                      
                      <Col span={6}>
                        <div>
                          <div style={{ marginBottom: 8 }}>转场类型:</div>
                          <Select
                            value={transition.type}
                            onChange={(value) => updateTransition(transition.id, { type: value })}
                            style={{ width: '100%' }}
                            size="small"
                          >
                            {transitionTypes.map(type => (
                              <Option key={type.id} value={type.id}>
                                <Tag color={type.color} size="small" style={{ marginRight: 8 }}>
                                  {type.preview}
                                </Tag>
                                {type.name}
                              </Option>
                            ))}
                          </Select>
                        </div>
                      </Col>
                      
                      <Col span={6}>
                        <div>
                          <div style={{ marginBottom: 8 }}>
                            持续时间: {transition.duration}s
                          </div>
                          <Slider
                            min={transitionType?.duration[0] || 0.3}
                            max={transitionType?.duration[1] || 3}
                            step={0.1}
                            value={transition.duration}
                            onChange={(value) => updateTransition(transition.id, { duration: value })}
                          />
                        </div>
                      </Col>
                      
                      <Col span={6}>
                        <div>
                          <div style={{ marginBottom: 8 }}>缓动:</div>
                          <Select
                            value={transition.easing}
                            onChange={(value) => updateTransition(transition.id, { easing: value })}
                            style={{ width: '100%' }}
                            size="small"
                          >
                            <Option value="linear">线性</Option>
                            <Option value="ease">缓动</Option>
                            <Option value="ease-in">缓入</Option>
                            <Option value="ease-out">缓出</Option>
                            <Option value="ease-in-out">缓入缓出</Option>
                          </Select>
                        </div>
                      </Col>
                    </Row>
                    
                    <Row style={{ width: '100%', marginTop: 12 }}>
                      <Col span={24}>
                        <Space>
                          <Button
                            size="small"
                            icon={<PlayCircleOutlined />}
                            onClick={(e) => {
                              e.stopPropagation();
                              previewTransition(transition);
                            }}
                          >
                            预览
                          </Button>
                          
                          <Button
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              applyToAll('type', transition.type);
                            }}
                          >
                            应用类型到全部
                          </Button>
                          
                          <Button
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              applyToAll('duration', transition.duration);
                            }}
                          >
                            应用时长到全部
                          </Button>
                        </Space>
                      </Col>
                    </Row>
                  </List.Item>
                );
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* 全局设置 */}
      <Card title="全局转场设置" style={{ marginTop: 16 }}>
        <Row gutter={[16, 16]}>
          <Col span={8}>
            <div>
              <div style={{ marginBottom: 8 }}>默认转场类型:</div>
              <Select
                placeholder="选择默认转场"
                style={{ width: '100%' }}
                onChange={(value) => applyToAll('type', value)}
              >
                {transitionTypes.map(type => (
                  <Option key={type.id} value={type.id}>
                    <Tag color={type.color} size="small" style={{ marginRight: 8 }}>
                      {type.preview}
                    </Tag>
                    {type.name}
                  </Option>
                ))}
              </Select>
            </div>
          </Col>
          
          <Col span={8}>
            <div>
              <div style={{ marginBottom: 8 }}>默认持续时间: 1.0s</div>
              <Slider
                min={0.3}
                max={3}
                step={0.1}
                defaultValue={1.0}
                onChange={(value) => applyToAll('duration', value)}
              />
            </div>
          </Col>
          
          <Col span={8}>
            <div>
              <div style={{ marginBottom: 8 }}>默认缓动:</div>
              <Select
                defaultValue="ease-in-out"
                style={{ width: '100%' }}
                onChange={(value) => applyToAll('easing', value)}
              >
                <Option value="linear">线性</Option>
                <Option value="ease">缓动</Option>
                <Option value="ease-in">缓入</Option>
                <Option value="ease-out">缓出</Option>
                <Option value="ease-in-out">缓入缓出</Option>
              </Select>
            </div>
          </Col>
        </Row>
      </Card>

      {/* 转场统计 */}
      <Card title="转场统计" style={{ marginTop: 16 }}>
        <Row gutter={[16, 16]}>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>
                {transitions.length}
              </div>
              <div style={{ color: '#666' }}>总转场数</div>
            </div>
          </Col>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>
                {(transitions.reduce((sum, t) => sum + t.duration, 0)).toFixed(1)}s
              </div>
              <div style={{ color: '#666' }}>总转场时长</div>
            </div>
          </Col>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#fa8c16' }}>
                {new Set(transitions.map(t => t.type)).size}
              </div>
              <div style={{ color: '#666' }}>使用效果数</div>
            </div>
          </Col>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#eb2f96' }}>
                {(transitions.reduce((sum, t) => sum + t.duration, 0) / transitions.length).toFixed(1)}s
              </div>
              <div style={{ color: '#666' }}>平均时长</div>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
}

export default TransitionEditor;