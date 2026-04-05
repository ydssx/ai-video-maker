import React, { useState } from 'react';
import { Card, Button, Space, message } from 'antd';
import TemplateSelector from './TemplateSelector';

const TemplateTest = () => {
  const [selectedTemplate, setSelectedTemplate] = useState('default');

  const handleTemplateChange = (templateId) => {
    console.log('模板变更测试:', templateId);
    setSelectedTemplate(templateId);
    message.success(`已选择模板: ${templateId}`);
  };

  const handleReset = () => {
    setSelectedTemplate('default');
    message.info('已重置为默认模板');
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card title="模板选择器测试" style={{ marginBottom: '16px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <strong>当前选中的模板:</strong> {selectedTemplate}
          </div>
          <Button onClick={handleReset}>重置为默认模板</Button>
        </Space>
      </Card>

      <Card title="模板选择器">
        <TemplateSelector
          selectedTemplate={selectedTemplate}
          onTemplateChange={handleTemplateChange}
        />
      </Card>
    </div>
  );
};

export default TemplateTest;