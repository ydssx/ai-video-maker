import React, { useState, useEffect } from 'react';
import { Form, Input, Select, Button, Card, Tag, Spin, Alert, Row, Col, Tooltip, Space, message } from 'antd';
import { PlayCircleOutlined, EditOutlined, BulbOutlined, ReloadOutlined, EyeOutlined } from '@ant-design/icons';
import axios from 'axios';
import { ScriptGeneratingLoader } from './LoadingStates';
import { ScriptTips } from './HelpTips';

const { TextArea } = Input;
const { Option } = Select;

function ScriptGenerator({ onScriptGenerated }) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [script, setScript] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

  const handleSubmit = async (values) => {
    setLoading(true);
    setScript(null); // 清除之前的脚本
    
    try {
      // 模拟进度更新
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) {
          clearInterval(progressInterval);
        }
      }, 500);

      const response = await axios.post('/api/script/generate', values);
      
      clearInterval(progressInterval);
      setScript(response.data);
      onScriptGenerated(response.data);
      
      // 记录统计
      try {
        await axios.post('/api/stats/record-script');
      } catch (error) {
        console.warn('记录统计失败:', error);
      }
      
      // 显示成功消息
      message.success('脚本生成成功！');
      
    } catch (error) {
      console.error('脚本生成失败:', error);
      message.error('脚本生成失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
    generateSuggestions();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await axios.get('/api/script/templates');
      setTemplates(response.data.templates);
    } catch (error) {
      console.error('获取模板失败:', error);
    }
  };

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

  const handleSuggestionClick = (suggestion) => {
    form.setFieldsValue({ topic: suggestion });
  };

  const handleRegenerate = () => {
    form.submit();
  };

  const getStyleDescription = (style) => {
    const descriptions = {
      'educational': '适合知识分享、教程讲解，语言简洁明了',
      'entertainment': '适合搞笑段子、生活趣事，语言生动有趣',
      'commercial': '适合产品介绍、品牌宣传，突出优势特点',
      'news': '适合新闻资讯、时事评论，客观准确表达'
    };
    return descriptions[style] || '';
  };

  const getDurationDescription = (duration) => {
    const descriptions = {
      '15s': '快速传达核心信息，适合抖音等短视频平台',
      '30s': '平衡内容深度与观看体验，最受欢迎的时长',
      '60s': '深入展开话题，适合教学和详细介绍'
    };
    return descriptions[duration] || '';
  };

  // 如果正在加载，显示加载状态
  if (loading) {
    return <ScriptGeneratingLoader progress={Math.random() * 100} />;
  }

  return (
    <div className="script-form">
      <Row gutter={[24, 24]}>
        <Col span={16}>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            initialValues={{
              style: 'educational',
              duration: '30s',
              language: 'zh'
            }}
          >
            <Form.Item
              label="视频主题"
              name="topic"
              rules={[{ required: true, message: '请输入视频主题' }]}
            >
              <Input 
                placeholder="例如：Python 编程入门、健康饮食知识、旅游攻略等"
                size="large"
              />
            </Form.Item>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="视频风格"
                  name="style"
                >
                  <Select 
                    size="large"
                    onChange={(value) => {
                      // 可以在这里添加风格变化的逻辑
                    }}
                  >
                    <Option value="educational">
                      <div>
                        <div>教育科普</div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          知识分享、教程讲解
                        </div>
                      </div>
                    </Option>
                    <Option value="entertainment">
                      <div>
                        <div>娱乐搞笑</div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          搞笑段子、生活趣事
                        </div>
                      </div>
                    </Option>
                    <Option value="commercial">
                      <div>
                        <div>商业推广</div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          产品介绍、品牌宣传
                        </div>
                      </div>
                    </Option>
                    <Option value="news">
                      <div>
                        <div>新闻资讯</div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          新闻资讯、时事评论
                        </div>
                      </div>
                    </Option>
                  </Select>
                </Form.Item>
              </Col>

              <Col span={12}>
                <Form.Item
                  label="视频时长"
                  name="duration"
                >
                  <Select size="large">
                    <Option value="15s">
                      <div>
                        <div>15秒</div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          快速传达，适合抖音
                        </div>
                      </div>
                    </Option>
                    <Option value="30s">
                      <div>
                        <div>30秒</div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          平衡深度，最受欢迎
                        </div>
                      </div>
                    </Option>
                    <Option value="60s">
                      <div>
                        <div>60秒</div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          深入展开，详细介绍
                        </div>
                      </div>
                    </Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Form.Item>
              <Space size="middle" style={{ width: '100%' }}>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  size="large"
                  icon={<EditOutlined />}
                  style={{ flex: 1 }}
                >
                  {loading ? '生成中...' : '生成脚本'}
                </Button>
                {script && (
                  <Tooltip title="重新生成脚本">
                    <Button 
                      size="large"
                      icon={<ReloadOutlined />}
                      onClick={handleRegenerate}
                      loading={loading}
                    />
                  </Tooltip>
                )}
              </Space>
            </Form.Item>
          </Form>
        </Col>

        <Col span={8}>
          <Card title="主题建议" size="small" style={{ height: 'fit-content' }}>
            <div style={{ marginBottom: 12 }}>
              <BulbOutlined style={{ color: '#faad14', marginRight: 8 }} />
              <span style={{ fontSize: '12px', color: '#666' }}>
                点击下方主题快速填入
              </span>
            </div>
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  type="text"
                  size="small"
                  onClick={() => handleSuggestionClick(suggestion)}
                  style={{ 
                    textAlign: 'left', 
                    height: 'auto',
                    padding: '4px 8px',
                    width: '100%'
                  }}
                >
                  {suggestion}
                </Button>
              ))}
            </Space>
            <Button 
              type="link" 
              size="small" 
              onClick={generateSuggestions}
              style={{ padding: 0, marginTop: 8 }}
            >
              换一批建议
            </Button>
          </Card>

          {templates.length > 0 && (
            <Card title="脚本模板" size="small" style={{ marginTop: 16 }}>
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                {templates.map((template, index) => (
                  <div key={index} style={{ 
                    padding: '8px', 
                    border: '1px solid #f0f0f0', 
                    borderRadius: '4px',
                    fontSize: '12px'
                  }}>
                    <div style={{ fontWeight: 'bold', marginBottom: 4 }}>
                      {template.name}
                    </div>
                    <div style={{ color: '#666' }}>
                      {template.description}
                    </div>
                    <div style={{ marginTop: 4, color: '#1890ff' }}>
                      示例：{template.example_topics?.[0]}
                    </div>
                  </div>
                ))}
              </Space>
            </Card>
          )}

          <ScriptTips />
        </Col>
      </Row>

      {script && (
        <Card 
          title={
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span>脚本预览：{script.title}</span>
              <Space>
                <Tag color="blue">总时长: {script.total_duration}秒</Tag>
                <Tag color="green">场景数: {script.scenes.length}</Tag>
                <Tag color="orange">风格: {script.style}</Tag>
              </Space>
            </div>
          }
          style={{ marginTop: 20 }}
          extra={
            <Space>
              <Tooltip title="预览脚本效果">
                <Button 
                  type="text"
                  icon={<EyeOutlined />}
                  onClick={() => {
                    // 可以添加脚本预览功能
                  }}
                />
              </Tooltip>
              <Button 
                type="link" 
                onClick={handleRegenerate}
                loading={loading}
                icon={<ReloadOutlined />}
              >
                重新生成
              </Button>
            </Space>
          }
        >
          <Row gutter={[16, 16]}>
            {script.scenes.map((scene, index) => (
              <Col span={24} key={index}>
                <Card 
                  size="small"
                  className="scene-card"
                  style={{ 
                    background: index % 2 === 0 ? '#fafafa' : '#ffffff',
                    border: '1px solid #f0f0f0'
                  }}
                >
                  <Row gutter={16}>
                    <Col span={2}>
                      <div style={{
                        width: 40,
                        height: 40,
                        borderRadius: '50%',
                        background: '#1890ff',
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 'bold'
                      }}>
                        {index + 1}
                      </div>
                    </Col>
                    <Col span={22}>
                      <div style={{ marginBottom: 8 }}>
                        <Tag color="purple" size="small">
                          {scene.duration}秒
                        </Tag>
                        <Tag color="geekblue" size="small">
                          {scene.transition}
                        </Tag>
                      </div>
                      <div style={{ 
                        fontSize: '16px', 
                        lineHeight: '1.5',
                        marginBottom: 12,
                        padding: '8px 12px',
                        background: 'white',
                        borderRadius: '4px',
                        border: '1px solid #e8e8e8'
                      }}>
                        {scene.text}
                      </div>
                      <div>
                        <span style={{ fontSize: '12px', color: '#666', marginRight: 8 }}>
                          关键词：
                        </span>
                        {scene.image_keywords.map(keyword => (
                          <Tag key={keyword} color="cyan" size="small">
                            {keyword}
                          </Tag>
                        ))}
                      </div>
                    </Col>
                  </Row>
                </Card>
              </Col>
            ))}
          </Row>

          <div style={{ marginTop: 20, textAlign: 'center' }}>
            <Alert
              message="脚本生成完成"
              description={
                <div>
                  <p>您的脚本已经生成完成！包含 {script.scenes.length} 个场景，总时长 {script.total_duration} 秒。</p>
                  <p>您可以继续下一步选择模板和语音，或重新生成脚本进行调整。</p>
                </div>
              }
              type="success"
              showIcon
              action={
                <Button 
                  type="primary" 
                  size="small"
                  onClick={() => onScriptGenerated(script)}
                >
                  继续制作视频
                </Button>
              }
            />
          </div>
        </Card>
      )}
    </div>
  );
}

export default ScriptGenerator;