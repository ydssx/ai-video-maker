import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Input, 
  Select, 
  Button, 
  Card, 
  Row, 
  Col, 
  Space, 
  Typography, 
  Divider,
  message,
  Spin,
  Tooltip,
  Badge
} from 'antd';
import { 
  PlayCircleOutlined, 
  BulbOutlined, 
  ReloadOutlined, 
  FileTextOutlined,
  ClockCircleOutlined,
  StarOutlined,
  FireOutlined
} from '@ant-design/icons';
import axios from 'axios';
import './OptimizedScriptGenerator.css';

const { TextArea } = Input;
const { Option } = Select;
const { Title, Text, Paragraph } = Typography;

const OptimizedScriptGenerator = ({ onScriptGenerated }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [script, setScript] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [selectedStyle, setSelectedStyle] = useState('educational');
  const [selectedDuration, setSelectedDuration] = useState('30s');

  const styleOptions = [
    { 
      value: 'educational', 
      label: '教育科普', 
      description: '知识分享、教程讲解',
      icon: '📚',
      color: '#1890ff'
    },
    { 
      value: 'entertainment', 
      label: '娱乐搞笑', 
      description: '搞笑段子、生活趣事',
      icon: '😄',
      color: '#52c41a'
    },
    { 
      value: 'commercial', 
      label: '商业推广', 
      description: '产品介绍、品牌宣传',
      icon: '💼',
      color: '#fa8c16'
    },
    { 
      value: 'news', 
      label: '新闻资讯', 
      description: '时事评论、热点分析',
      icon: '📰',
      color: '#722ed1'
    }
  ];

  const durationOptions = [
    { value: '15s', label: '15秒', description: '简洁明了，快速传达', color: '#52c41a' },
    { value: '30s', label: '30秒', description: '平衡深度，最受欢迎', color: '#1890ff' },
    { value: '60s', label: '60秒', description: '详细讲解，深度内容', color: '#fa8c16' }
  ];

  useEffect(() => {
    generateSuggestions();
  }, []);

  const generateSuggestions = () => {
    const topicSuggestions = [
      "Python 编程入门",
      "健康饮食小贴士",
      "旅游攻略分享",
      "理财投资基础",
      "摄影技巧教学",
      "美食制作教程",
      "运动健身指南",
      "科技产品评测",
      "生活小妙招",
      "学习方法分享"
    ];
    setSuggestions(topicSuggestions.sort(() => Math.random() - 0.5).slice(0, 5));
  };

  const handleSubmit = async (values) => {
    setLoading(true);
    setScript(null);
    
    try {
      const response = await axios.post('/api/script/generate', {
        topic: values.topic,
        style: selectedStyle,
        duration: selectedDuration,
        language: 'zh'
      });
      
      setScript(response.data);
      onScriptGenerated(response.data);
      message.success('脚本生成成功！');
      
      // 记录统计
      try {
        await axios.post('/api/stats/record-script');
      } catch (error) {
        console.warn('记录统计失败:', error);
      }
      
    } catch (error) {
      console.error('脚本生成失败:', error);
      message.error('脚本生成失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    form.setFieldsValue({ topic: suggestion });
  };

  const handleStyleSelect = (style) => {
    setSelectedStyle(style);
  };

  const handleDurationSelect = (duration) => {
    setSelectedDuration(duration);
  };

  return (
    <div className="optimized-script-generator">
      <div className="generator-header">
        <Title level={2} className="main-title">
          🎬 AI 智能脚本生成
        </Title>
        <Text className="subtitle">
          让创意更简单，让内容更精彩
        </Text>
      </div>

      <Row gutter={[24, 24]}>
        {/* 主内容区域 */}
        <Col xs={24} lg={16}>
          <Card className="main-content-card" bordered={false}>
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
                             initialValues={{
                 topic: '旅游攻略分享',
                 style: 'educational',
                 duration: '30s'
               }}
            >
              {/* 视频主题输入 */}
              <div className="input-section">
                <Form.Item
                  name="topic"
                  label={
                    <Space>
                      <span className="label-icon">🎯</span>
                      <span>视频主题</span>
                    </Space>
                  }
                  rules={[{ required: true, message: '请输入视频主题' }]}
                >
                  <Input 
                    size="large"
                    placeholder="输入您想要制作的视频主题..."
                    className="topic-input"
                  />
                </Form.Item>
                <Text className="input-hint">
                  建议使用具体、描述性的主题，让 AI 更好地理解您的需求
                </Text>
              </div>

              {/* 风格和时长选择 */}
              <div className="selection-section">
                <Row gutter={[16, 16]}>
                  <Col xs={24} md={12}>
                    <div className="style-selector">
                      <Text strong className="section-label">
                        <span className="label-icon">🎨</span>
                        视频风格
                      </Text>
                      <div className="style-options">
                        {styleOptions.map((style) => (
                          <div
                            key={style.value}
                            className={`style-option ${selectedStyle === style.value ? 'selected' : ''}`}
                            onClick={() => handleStyleSelect(style.value)}
                            style={{ borderColor: selectedStyle === style.value ? style.color : undefined }}
                          >
                            <span className="style-icon">{style.icon}</span>
                            <div className="style-info">
                              <Text strong className="style-label">{style.label}</Text>
                              <Text className="style-description">{style.description}</Text>
                            </div>
                            {selectedStyle === style.value && (
                              <Badge 
                                status="processing" 
                                color={style.color}
                                className="selection-badge"
                              />
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </Col>

                  <Col xs={24} md={12}>
                    <div className="duration-selector">
                      <Text strong className="section-label">
                        <span className="label-icon">⏱️</span>
                        视频时长
                      </Text>
                      <div className="duration-options">
                        {durationOptions.map((duration) => (
                          <div
                            key={duration.value}
                            className={`duration-option ${selectedDuration === duration.value ? 'selected' : ''}`}
                            onClick={() => handleDurationSelect(duration.value)}
                            style={{ borderColor: selectedDuration === duration.value ? duration.color : undefined }}
                          >
                            <div className="duration-content">
                              <Text strong className="duration-value">{duration.label}</Text>
                              <Text className="duration-description">{duration.description}</Text>
                            </div>
                            {selectedDuration === duration.value && (
                              <Badge 
                                status="processing" 
                                color={duration.color}
                                className="selection-badge"
                              />
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </Col>
                </Row>
              </div>

              {/* 生成按钮 */}
              <div className="action-section">
                <Button
                  type="primary"
                  size="large"
                  htmlType="submit"
                  loading={loading}
                  icon={<PlayCircleOutlined />}
                  className="generate-button"
                >
                  {loading ? '正在生成中...' : '✨ 生成脚本'}
                </Button>
              </div>
            </Form>
          </Card>
        </Col>

        {/* 右侧边栏 */}
        <Col xs={24} lg={8}>
          <div className="sidebar">
            {/* 主题建议 */}
            <Card className="sidebar-card" bordered={false}>
              <div className="card-header">
                <BulbOutlined className="card-icon" />
                <Text strong>主题建议</Text>
              </div>
              <Text className="card-hint">点击下方主题快速填入</Text>
              <div className="suggestions-list">
                {suggestions.map((suggestion, index) => (
                  <Button
                    key={index}
                    type="text"
                    className="suggestion-item"
                    onClick={() => handleSuggestionClick(suggestion)}
                    icon={<StarOutlined />}
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
              <Button
                type="link"
                icon={<ReloadOutlined />}
                onClick={generateSuggestions}
                className="refresh-button"
              >
                换一批建议
              </Button>
            </Card>

            {/* 脚本模板 */}
            <Card className="sidebar-card" bordered={false}>
              <div className="card-header">
                <FileTextOutlined className="card-icon" />
                <Text strong>脚本模板</Text>
              </div>
              <div className="template-categories">
                {styleOptions.map((style) => (
                  <div key={style.value} className="template-category">
                    <div className="category-header">
                      <span className="category-icon">{style.icon}</span>
                      <Text strong className="category-name">{style.label}</Text>
                    </div>
                    <Text className="category-description">{style.description}</Text>
                    <div className="template-example">
                      示例: {style.value === 'educational' ? 'Python 编程入门' : 
                             style.value === 'entertainment' ? '程序员的日常' : 
                             style.value === 'commercial' ? '新产品发布' : '时事热点分析'}
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* 创作小贴士 */}
            <Card className="sidebar-card" bordered={false}>
              <div className="card-header">
                <BulbOutlined className="card-icon" />
                <Text strong>创作小贴士</Text>
              </div>
              <div className="tips-list">
                <div className="tip-item">
                  <FireOutlined className="tip-icon" />
                  <Text>主题选择技巧</Text>
                </div>
                <div className="tip-item">
                  <FireOutlined className="tip-icon" />
                  <Text>风格选择指南</Text>
                </div>
                <div className="tip-item">
                  <FireOutlined className="tip-icon" />
                  <Text>时长建议</Text>
                </div>
              </div>
            </Card>
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default OptimizedScriptGenerator;
