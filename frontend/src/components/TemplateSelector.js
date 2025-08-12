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
      const response = await axios.get('/api/video/templates');
      setTemplates(response.data.templates);
    } catch (error) {
      console.error('获取模板失败:', error);
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
      <h4>选择视频模板</h4>
      
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
            <Card
              hoverable
              className={`template-card ${selectedTemplate === template.id ? 'template-selected' : ''}`}
              style={{ position: 'relative' }}
              onClick={() => onTemplateChange(template.id)}
            >
              {selectedTemplate === template.id && (
                <div className="template-check">
                  <CheckOutlined style={{ color: 'white', fontSize: 12 }} />
                </div>
              )}
              
              <div className="template-preview" style={{ 
                background: getTemplatePreview(template),
                color: getTextColor(template)
              }}>
                <span style={{ position: 'relative', zIndex: 1 }}>示例文字</span>
              </div>
              
              <div className="template-info">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <strong>{template.name}</strong>
                  <Tag color={getCategoryColor(template.category)}>{template.category}</Tag>
                </div>
                <p style={{ fontSize: 12, color: '#666', margin: 0 }}>
                  {template.description}
                </p>
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}

export default TemplateSelector;