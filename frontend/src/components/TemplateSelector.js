import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Tag, Tabs } from 'antd';
import { CheckOutlined } from '@ant-design/icons';
import axios from 'axios';

const { TabPane } = Tabs;

function TemplateSelector({ selectedTemplate, onTemplateChange }) {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('全部');

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      console.log('正在获取模板...');
      const response = await axios.get('/api/video/templates');
      console.log('模板数据:', response.data);
      setTemplates(response.data.templates);
    } catch (error) {
      console.error('获取模板失败:', error);
      // 如果API失败，使用默认模板
      const defaultTemplates = [
        {
          id: 'default',
          name: '默认模板',
          description: '经典的白色文字居中显示，适合各种内容',
          category: '通用'
        },
        {
          id: 'modern',
          name: '现代模板',
          description: '简洁现代的设计风格，适合商务和科技内容',
          category: '通用'
        }
      ];
      setTemplates(defaultTemplates);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      '通用': 'blue',
      '商务': 'green',
      '生活': 'orange',
      '教育': 'purple'
    };
    return colors[category] || 'default';
  };

  const getFilteredTemplates = (category) => {
    if (category === '全部') return templates;
    return templates.filter(template => template.category === category);
  };

  const getCategories = () => {
    const categories = ['全部', ...new Set(templates.map(t => t.category))];
    return categories;
  };

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

  if (loading) {
    return <div>加载模板中...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h4 style={{ margin: 0 }}>选择视频模板</h4>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ fontSize: '12px', color: '#666' }}>
            当前选中: {selectedTemplate || '无'}
          </div>
          <button
            style={{
              padding: '4px 8px',
              fontSize: '12px',
              border: '1px solid #d9d9d9',
              borderRadius: '4px',
              background: 'white',
              cursor: 'pointer'
            }}
            onClick={() => {
              console.log('测试按钮点击');
              if (onTemplateChange) {
                onTemplateChange('modern');
                console.log('测试调用成功');
              } else {
                console.error('onTemplateChange 未定义');
              }
            }}
          >
            测试
          </button>
        </div>
      </div>
      
      <Tabs 
        activeKey={selectedCategory} 
        onChange={setSelectedCategory}
        size="small"
        style={{ marginBottom: 16 }}
      >
        {getCategories().map(category => (
          <TabPane 
            tab={`${category} (${getFilteredTemplates(category).length})`} 
            key={category}
          />
        ))}
      </Tabs>

      <Row gutter={[16, 16]}>
        {getFilteredTemplates(selectedCategory).map(template => (
          <Col span={12} key={template.id}>
            <div
              className={`template-card ${selectedTemplate === template.id ? 'template-selected' : ''}`}
              style={{ 
                position: 'relative',
                cursor: 'pointer',
                border: selectedTemplate === template.id ? '2px solid #1890ff' : '1px solid #d9d9d9',
                borderRadius: '8px',
                overflow: 'hidden',
                transition: 'all 0.3s ease',
                backgroundColor: 'white',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('模板点击:', template.id, template.name);
                if (onTemplateChange) {
                  onTemplateChange(template.id);
                } else {
                  console.error('onTemplateChange 函数未定义');
                }
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
              }}
            >
              {selectedTemplate === template.id && (
                <div style={{
                  position: 'absolute',
                  top: '8px',
                  right: '8px',
                  width: '20px',
                  height: '20px',
                  background: '#1890ff',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 2
                }}>
                  <CheckOutlined style={{ color: 'white', fontSize: 12 }} />
                </div>
              )}
              
              <div style={{ 
                height: '80px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: 'bold',
                position: 'relative',
                overflow: 'hidden',
                background: getTemplatePreview(template),
                color: getTextColor(template)
              }}>
                <span style={{ position: 'relative', zIndex: 1 }}>示例文字</span>
              </div>
              
              <div style={{ padding: '12px', background: 'white' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <strong style={{ color: '#262626', fontSize: '14px' }}>{template.name}</strong>
                  <Tag color={getCategoryColor(template.category)}>{template.category}</Tag>
                </div>
                <p style={{ fontSize: 12, color: '#8c8c8c', margin: 0, lineHeight: 1.4 }}>
                  {template.description}
                </p>
              </div>
            </div>
          </Col>
        ))}
      </Row>
    </div>
  );
}

export default TemplateSelector;