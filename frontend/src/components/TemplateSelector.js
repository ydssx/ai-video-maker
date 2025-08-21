import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, Row, Col, Tag, Tabs, Skeleton, Empty, Input, Button, Space, Tooltip, message, Result } from 'antd';
import { CheckOutlined, ReloadOutlined, SearchOutlined, EyeOutlined, CheckCircleOutlined } from '@ant-design/icons';
import api from '../utils/api';
import { t } from '../utils/i18n';

const { TabPane } = Tabs;

function TemplateSelector({ selectedTemplate, onTemplateChange }) {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('全部');
  const [searchText, setSearchText] = useState('');
  const [previewTemplate, setPreviewTemplate] = useState(null);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get('/video/templates');
      setTemplates(data.templates || []);
    } catch (err) {
      setError('模板加载失败');
      // 回退到内置默认模板，保证可继续
      const defaultTemplates = [
        { id: 'default', name: '默认模板', description: '经典的白色文字居中显示，适合各种内容', category: '通用' },
        { id: 'modern', name: '现代模板', description: '简洁现代的设计风格，适合商务和科技内容', category: '通用' }
      ];
      setTemplates(defaultTemplates);
      message.warning('模板服务不可用，已使用默认模板');
    } finally {
      setLoading(false);
    }
  }, []);

  const getCategoryColor = (category) => {
    const colors = {
      '通用': 'blue',
      '商务': 'green',
      '生活': 'orange',
      '教育': 'purple'
    };
    return colors[category] || 'default';
  };

  const getFilteredTemplates = useCallback((category) => {
    const pool = category === '全部' ? templates : templates.filter(t => t.category === category);
    if (!searchText) return pool;
    const q = searchText.toLowerCase();
    return pool.filter(t =>
      (t.name || '').toLowerCase().includes(q) ||
      (t.description || '').toLowerCase().includes(q) ||
      (t.id || '').toLowerCase().includes(q)
    );
  }, [templates, searchText]);

  const categories = useMemo(() => ['全部', ...new Set(templates.map(t => t.category))], [templates]);

  const getTemplatePreview = (template) => {
    // 根据模板类型生成预览背景
    const previewMap = {
      // 基础模板
      'default': 'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)',
      'modern': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      'tech': 'linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%)',
      'elegant': 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
      
      // 商务模板
      'corporate': 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)',
      'startup': 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)',
      'finance': 'linear-gradient(135deg, #1f2937 0%, #ffd700 100%)',
      'ecommerce': 'linear-gradient(135deg, #ec4899 0%, #f472b6 100%)',
      
      // 生活方式模板
      'food': 'linear-gradient(135deg, #dc2626 0%, #ea580c 100%)',
      'travel': 'linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)',
      'fitness': 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
      'beauty': 'linear-gradient(135deg, #db2777 0%, #e879f9 100%)',
      
      // 教育模板
      'academic': 'linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%)',
      'kids': 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
      'language': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
      'skill': 'linear-gradient(135deg, #ea580c 0%, #dc2626 100%)'
    };
    
    return previewMap[template.id] || previewMap['default'];
  };

  const getTextColor = (template) => {
    // 根据模板类型设置文字颜色
    const colorMap = {
      'modern': '#2D2D2D',
      'tech': '#00FFFF',
      'elegant': '#8B4513',
      'finance': '#FFD700',
      'kids': '#FFFFFF'
    };
    
    return colorMap[template.id] || '#FFFFFF';
  };

  // 处理模板选择
  const handleTemplateSelect = useCallback((template) => {
    onTemplateChange(template.id);
    message.success(`已选择模板: ${template.name}`);
  }, [onTemplateChange]);

  // 处理模板预览
  const handleTemplatePreview = useCallback((template, e) => {
    e.stopPropagation();
    setPreviewTemplate(template);
  }, []);

  // 处理键盘操作
  const handleKeyDown = useCallback((e, template) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleTemplateSelect(template);
    }
  }, [handleTemplateSelect]);

  // 渲染模板卡片
  const renderTemplateCard = useCallback((template) => {
    const isSelected = selectedTemplate === template.id;
    
    return (
      <Col xs={24} sm={12} md={8} lg={6} key={template.id}>
        <Card
          className={`template-card ${isSelected ? 'template-selected' : ''}`}
          hoverable
          onClick={() => handleTemplateSelect(template)}
          onKeyDown={(e) => handleKeyDown(e, template)}
          tabIndex={0}
          role="button"
          aria-label={`选择模板: ${template.name}`}
          style={{ marginBottom: 16 }}
        >
          <div 
            className="template-preview"
            style={{ 
              background: getTemplatePreview(template),
              color: getTextColor(template)
            }}
          >
            {template.name}
          </div>
          
          <div style={{ padding: '12px 0' }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>{template.name}</h4>
            <p style={{ margin: '0 0 12px 0', color: '#666', fontSize: '14px' }}>
              {template.description}
            </p>
            
            <div style={{ marginBottom: 12 }}>
              <Tag color={getCategoryColor(template.category)}>{template.category}</Tag>
              {template.tags && template.tags.map(tag => (
                <Tag key={tag} size="small">{tag}</Tag>
              ))}
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Space>
                <Tooltip title="预览模板">
                  <Button
                    type="text"
                    size="small"
                    icon={<EyeOutlined />}
                    onClick={(e) => handleTemplatePreview(template, e)}
                    aria-label={`预览模板: ${template.name}`}
                  />
                </Tooltip>
                {isSelected && (
                  <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '18px' }} />
                )}
              </Space>
              
              <Button
                type={isSelected ? 'primary' : 'default'}
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleTemplateSelect(template);
                }}
              >
                {isSelected ? '已选择' : '选择'}
              </Button>
            </div>
          </div>
        </Card>
      </Col>
    );
  }, [selectedTemplate, handleTemplateSelect, handleKeyDown, handleTemplatePreview]);

  // 渲染加载状态
  if (loading) {
    return (
      <div style={{ padding: '24px' }}>
        <Skeleton active paragraph={{ rows: 4 }} />
      </div>
    );
  }

  // 渲染错误状态
  if (error) {
    return (
      <Result
        status="error"
        title="模板加载失败"
        subTitle="无法连接到模板服务，请检查网络连接"
        extra={[
          <Button key="retry" type="primary" onClick={fetchTemplates}>
            重试
          </Button>,
          <Button key="default" onClick={() => {
            const defaultTemplate = { id: 'default', name: '默认模板', description: '经典模板', category: '通用' };
            onTemplateChange(defaultTemplate.id);
            message.info('已使用默认模板');
          }}>
            使用默认模板
          </Button>
        ]}
      />
    );
  }

  // 渲染空状态
  if (templates.length === 0) {
    return (
      <Empty
        description="暂无可用模板"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      />
    );
  }

  return (
    <div>
      {/* 搜索和分类过滤 */}
      <div style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Input
              placeholder="搜索模板..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              allowClear
              style={{ maxWidth: 300 }}
            />
          </Col>
          <Col>
            <Tabs
              activeKey={selectedCategory}
              onChange={setSelectedCategory}
              size="small"
              style={{ marginBottom: 0 }}
            >
              {categories.map(category => (
                <TabPane tab={category} key={category} />
              ))}
            </Tabs>
          </Col>
        </Row>
      </div>

      {/* 模板列表 */}
      <Row gutter={16}>
        {getFilteredTemplates(selectedCategory).map(renderTemplateCard)}
      </Row>

      {/* 模板预览模态框 */}
      {previewTemplate && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={() => setPreviewTemplate(null)}
        >
          <div
            style={{
              background: 'white',
              padding: '24px',
              borderRadius: '8px',
              maxWidth: '80%',
              maxHeight: '80%',
              overflow: 'auto'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3>{previewTemplate.name}</h3>
            <p>{previewTemplate.description}</p>
            <div
              style={{
                background: getTemplatePreview(previewTemplate),
                color: getTextColor(previewTemplate),
                padding: '40px',
                textAlign: 'center',
                borderRadius: '8px',
                marginBottom: '16px'
              }}
            >
              <h2 style={{ margin: 0 }}>模板预览</h2>
              <p style={{ margin: '16px 0 0 0' }}>这是模板的视觉效果</p>
            </div>
            <Button type="primary" onClick={() => handleTemplateSelect(previewTemplate)}>
              选择此模板
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default TemplateSelector;