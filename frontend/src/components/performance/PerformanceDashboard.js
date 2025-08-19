import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Button, Space, Progress, Tabs, Select, DatePicker, Tooltip, Badge } from 'antd';
import { 
  ArrowUpOutlined, 
  ArrowDownOutlined, 
  ReloadOutlined, 
  InfoCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined
} from '@ant-design/icons';
import { Line, Pie } from '@ant-design/plots';
import moment from 'moment';
import './PerformanceDashboard.css';

const { TabPane } = Tabs;
const { Option } = Select;
const { RangePicker } = DatePicker;

// 模拟API数据
const fetchPerformanceData = async () => {
  // 实际项目中这里应该是API调用
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        apiResponseTime: 320,
        cacheHitRate: 87,
        activeTasks: 12,
        totalTasks: 50,
        responseTimeTrend: Array.from({ length: 24 }, (_, i) => ({
          time: moment().subtract(23 - i, 'hours').format('HH:00'),
          value: Math.floor(Math.random() * 100) + 200,
        })),
        cacheDistribution: [
          { type: 'Templates', value: 27 },
          { type: 'Assets', value: 35 },
          { type: 'User Data', value: 25 },
          { type: 'System', value: 13 },
        ],
      });
    }, 500);
  });
};

// 状态标签组件
const StatusTag = ({ status }) => {
  const statusMap = {
    completed: {
      color: 'success',
      icon: <CheckCircleOutlined />,
      text: '已完成'
    },
    processing: {
      color: 'processing',
      icon: <SyncOutlined spin />,
      text: '进行中'
    },
    failed: {
      color: 'error',
      icon: <CloseCircleOutlined />,
      text: '失败'
    }
  };

  const statusInfo = statusMap[status] || statusMap.processing;
  
  return (
    <span>
      <Badge status={statusInfo.color} text={statusInfo.text} />
      {statusInfo.icon}
    </span>
  );
};

const PerformanceDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    apiResponseTime: 0,
    cacheHitRate: 0,
    activeTasks: 0,
    totalTasks: 0,
    responseTimeTrend: [],
    cacheDistribution: [],
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const result = await fetchPerformanceData();
      setData(result);
    } catch (error) {
      console.error('Failed to load performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const responseTimeConfig = {
    data: data.responseTimeTrend,
    xField: 'time',
    yField: 'value',
    point: {
      size: 5,
      shape: 'diamond',
    },
    label: {},
    smooth: true,
    yAxis: {
      label: {
        formatter: (v) => `${v}ms`,
      },
    },
  };

  const cacheConfig = {
    data: data.cacheDistribution,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
    interactions: [{ type: 'element-active' }],
  };

  const columns = [
    {
      title: '任务ID',
      dataIndex: 'id',
      key: 'id',
      width: 180,
      render: (text) => (
        <Tooltip title={text}>
          <span className="text-ellipsis">{text}</span>
        </Tooltip>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      filters: [
        { text: '视频导出', value: '视频导出' },
        { text: 'AI脚本生成', value: 'AI脚本生成' },
        { text: '视频转码', value: '视频转码' },
      ],
      onFilter: (value, record) => record.type === value,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      filters: [
        { text: '进行中', value: 'processing' },
        { text: '已完成', value: 'completed' },
        { text: '失败', value: 'failed' },
      ],
      onFilter: (value, record) => record.status === value,
      render: (status) => <StatusTag status={status} />,
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress) => (
        <Progress percent={progress} size="small" status={progress === 100 ? 'success' : 'active'} />
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button type="link" size="small">
            详情
          </Button>
          {record.status !== 'completed' && (
            <Button type="link" danger size="small">
              取消
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const taskData = [
    {
      key: '1',
      id: 'TASK-20230818-001',
      type: '视频导出',
      status: 'processing',
      progress: 65,
    },
    {
      key: '2',
      id: 'TASK-20230818-002',
      type: 'AI脚本生成',
      status: 'completed',
      progress: 100,
    },
    {
      key: '3',
      id: 'TASK-20230818-003',
      type: '视频转码',
      status: 'processing',
      progress: 30,
    },
  ];

  // 处理时间范围变化
  const handleDateChange = (dates) => {
    console.log('日期范围变化:', dates);
    // 这里可以添加加载新数据的逻辑
  };

  // 处理刷新数据
  const handleRefresh = () => {
    loadData();
  };

  return (
    <div className="performance-dashboard">
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>性能监控面板</h2>
        <Space>
          <RangePicker 
            showTime 
            onChange={handleDateChange}
            ranges={{
              '今天': [moment().startOf('day'), moment().endOf('day')],
              '本周': [moment().startOf('week'), moment().endOf('week')],
              '本月': [moment().startOf('month'), moment().endOf('month')],
            }}
            style={{ width: 360 }}
          />
          <Button 
            type="primary" 
            icon={<ReloadOutlined />} 
            onClick={handleRefresh} 
            loading={loading}
          >
            刷新数据
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Statistic
                title={
                  <span>
                    API平均响应时间
                    <Tooltip title="过去24小时API接口平均响应时间">
                      <InfoCircleOutlined style={{ marginLeft: 8, color: '#999' }} />
                    </Tooltip>
                  </span>
                }
                value={data.apiResponseTime}
                precision={0}
                valueStyle={{ color: data.apiResponseTime > 500 ? '#f5222d' : '#52c41a' }}
                suffix="ms"
              />
              <div style={{ fontSize: 24, color: data.apiResponseTime > 500 ? '#f5222d' : '#52c41a' }}>
                {data.apiResponseTime > 500 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              </div>
            </div>
            <div style={{ marginTop: 8 }}>
              <span style={{ color: data.apiResponseTime > 500 ? '#f5222d' : '#52c41a' }}>
                {data.apiResponseTime > 500 ? (
                  <ArrowUpOutlined />
                ) : (
                  <ArrowDownOutlined />
                )}
                {Math.abs(500 - data.apiResponseTime)}ms
              </span>
              <span style={{ marginLeft: 8, color: '#999' }}>较上周</span>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span>缓存命中率</span>
                <span style={{ color: data.cacheHitRate > 80 ? '#52c41a' : '#faad14', fontWeight: 'bold' }}>
                  {data.cacheHitRate}%
                </span>
              </div>
              <Progress
                percent={data.cacheHitRate}
                status={data.cacheHitRate > 80 ? 'success' : 'normal'}
                strokeColor={data.cacheHitRate > 80 ? '#52c41a' : '#faad14'}
                showInfo={false}
                strokeWidth={8}
              />
              <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
                较昨日 {data.cacheHitRate > 80 ? '↑' : '↓'} {Math.abs(80 - data.cacheHitRate)}%
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <div>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: data.activeTasks > 10 ? '#f5222d' : '#1890ff' }}>
                {data.activeTasks}
                <span style={{ fontSize: 16, marginLeft: 8, color: '#999' }}>/ {data.totalTasks}</span>
              </div>
              <div style={{ marginTop: 8, color: '#666' }}>活跃任务</div>
              <div style={{ marginTop: 8 }}>
                <Progress 
                  percent={(data.activeTasks / data.totalTasks) * 100} 
                  showInfo={false}
                  status={data.activeTasks > 10 ? 'exception' : 'normal'}
                />
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ 
                display: 'inline-block',
                padding: '8px 16px',
                borderRadius: 20,
                background: data.activeTasks > 10 ? '#fff2f0' : '#f6ffed',
                border: `1px solid ${data.activeTasks > 10 ? '#ffccc7' : '#b7eb8f'}`,
                color: data.activeTasks > 10 ? '#f5222d' : '#52c41a',
                fontWeight: 'bold',
                fontSize: 18,
                marginBottom: 8
              }}>
                {data.activeTasks > 10 ? '系统繁忙' : '系统正常'}
              </div>
              <div style={{ color: '#666', fontSize: 12 }}>
                最后更新: {moment().format('YYYY-MM-DD HH:mm:ss')}
              </div>
              <div style={{ marginTop: 8 }}>
                <Button type="link" size="small" icon={<ReloadOutlined />} onClick={handleRefresh}>
                  刷新状态
                </Button>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      <Tabs defaultActiveKey="1" style={{ marginBottom: 16 }}>
        <TabPane tab="响应时间趋势" key="1">
          <Card loading={loading}>
            <div style={{ height: 400 }}>
              <Line {...responseTimeConfig} />
            </div>
          </Card>
        </TabPane>
        <TabPane tab="缓存分布" key="2">
          <Card loading={loading}>
            <div style={{ height: 400 }}>
              <Pie {...cacheConfig} />
            </div>
          </Card>
        </TabPane>
        <TabPane tab="任务队列" key="3">
          <Card loading={loading}>
            <Table
              columns={columns}
              dataSource={taskData}
              pagination={{ pageSize: 5 }}
              rowKey="key"
            />
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default PerformanceDashboard;
