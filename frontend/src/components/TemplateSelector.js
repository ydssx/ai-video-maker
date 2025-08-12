import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Button, Tag, Divider } from 'antd';
import { CheckOutlined } from '@ant-design/icons';
import axios from 'axios';

function TemplateSelector({ selectedTemplate, onTemplateChange }) {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);

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
      '科技': 'cyan',
      '生活': 'orange'
    };
    return colors[category] || 'default';
  };

  return (
    <div>
      <h4>选择视频模板</h4>
      <Row gutter={[16, 16]}>
        {templates.map(template => (
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

function getTemplatePreview(template) {
  // 根据模板设置生成预览背景
  if (template.id === 'modern') {
    return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
  } else if (template.id === 'tech') {
    return 'linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%)';
  } else if (template.id === 'elegant') {
    return 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)';
  }
  
  return 'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)';
}

function getTextColor(template) {
  if (template.id === 'modern') {
    return '#2D2D2D';
  } else if (template.id === 'tech') {
    return '#00FFFF';
  } else if (template.id === 'elegant') {
    return '#8B4513';
  }
  
  return '#FFFFFF';
}

export default TemplateSelector;