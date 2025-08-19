import React, { useState } from 'react';
import { Layout, Button, Drawer } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import PerformanceDashboard from './PerformanceDashboard';

const { Content } = Layout;

const PerformancePage = ({ onBack }) => {
  const [showDrawer, setShowDrawer] = useState(false);
  const [drawerContent, setDrawerContent] = useState(null);

  const openDrawer = (content) => {
    setDrawerContent(content);
    setShowDrawer(true);
  };

  return (
    <Layout className="performance-page">
      <div className="page-header">
        <Button 
          type="link" 
          icon={<ArrowLeftOutlined />} 
          onClick={onBack}
          style={{ marginRight: 16 }}
        >
          返回
        </Button>
        <h2 style={{ margin: 0 }}>系统性能监控</h2>
      </div>
      
      <Content style={{ padding: '24px', background: '#fff' }}>
        <PerformanceDashboard />
      </Content>

      <Drawer
        title="性能详情"
        placement="right"
        width={600}
        onClose={() => setShowDrawer(false)}
        open={showDrawer}
        destroyOnClose
      >
        {drawerContent}
      </Drawer>
    </Layout>
  );
};

export default PerformancePage;
