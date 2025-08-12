import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Button, 
  Modal, 
  Form, 
  Input, 
  Select, 
  Tag, 
  Popconfirm,
  message,
  Tooltip,
  Empty
} from 'antd';
import { 
  SaveOutlined, 
  PlayCircleOutlined, 
  EditOutlined, 
  DeleteOutlined,
  StarOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Option } = Select;
const { TextArea } = Input;

function PresetManager({ currentConfig, onApplyPreset }) {
  const [presets, setPresets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPreset, setEditingPreset] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchPresets();
  }, []);

  const fetchPresets = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/presets/');
      setPresets(response.data.presets);
    } catch (error) {
      console.error('获取预设失败:', error);
      message.error('获取预设失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePreset = async (values) => {
    try {
      const presetData = {
        ...values,
        template_id: currentConfig.template_id || 'default',
        voice_config: currentConfig.voice_config || {
          provider: 'gtts',
          voice: 'zh',
          speed: 1.0,
          enabled: true
        }
      };

      if (editingPreset) {
        await axios.put(`/api/presets/${editingPreset.id}`, presetData);
        message.success('预设更新成功');
      } else {
        await axios.post('/api/presets/', presetData);
        message.success('预设保存成功');
      }

      setModalVisible(false);
      setEditingPreset(null);
      form.resetFields();
      fetchPresets();
    } catch (error) {
      console.error('保存预设失败:', error);
      message.error('保存预设失败');
    }
  };

  const handleUsePreset = async (preset) => {
    try {
      await axios.post(`/api/presets/${preset.id}/use`);
      onApplyPreset(preset);
      message.success(`已应用预设：${preset.name}`);
    } catch (error) {
      console.error('应用预设失败:', error);
      message.error('应用预设失败');
    }
  };

  const handleDeletePreset = async (presetId) => {
    try {
      await axios.delete(`/api/presets/${presetId}`);
      message.success('预设删除成功');
      fetchPresets();
    } catch (error) {
      console.error('删除预设失败:', error);
      message.error('删除预设失败');
    }
  };

  const handleEditPreset = (preset) => {
    setEditingPreset(preset);
    form.setFieldsValue({
      name: preset.name,
      description: preset.description,
      style: preset.style,
      duration: preset.duration
    });
    setModalVisible(true);
  };

  const createDefaultPresets = async () => {
    try {
      const response = await axios.post('/api/presets/default/create');
      message.success(response.data.message);
      fetchPresets();
    } catch (error) {
      console.error('创建默认预设失败:', error);
      message.error('创建默认预设失败');
    }
  };

  const getStyleColor = (style) => {
    const colors = {
      'educational': 'blue',
      'entertainment': 'orange',
      'commercial': 'green',
      'news': 'purple'
    };
    return colors[style] || 'default';
  };

  const getDurationColor = (duration) => {
    const colors = {
      '15s': 'red',
      '30s': 'orange',
      '60s': 'green'
    };
    return colors[duration] || 'default';
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h4>视频预设</h4>
        <div>
          <Button 
            type="primary" 
            icon={<SaveOutlined />}
            onClick={() => setModalVisible(true)}
            style={{ marginRight: 8 }}
          >
            保存当前配置
          </Button>
          <Button 
            onClick={createDefaultPresets}
            size="small"
          >
            创建默认预设
          </Button>
        </div>
      </div>

      {presets.length === 0 ? (
        <Empty 
          description="暂无预设"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary" onClick={createDefaultPresets}>
            创建默认预设
          </Button>
        </Empty>
      ) : (
        <Row gutter={[16, 16]}>
          {presets.map(preset => (
            <Col span={12} key={preset.id}>
              <Card
                size="small"
                hoverable
                actions={[
                  <Tooltip title="使用预设">
                    <PlayCircleOutlined 
                      onClick={() => handleUsePreset(preset)}
                    />
                  </Tooltip>,
                  <Tooltip title="编辑预设">
                    <EditOutlined 
                      onClick={() => handleEditPreset(preset)}
                    />
                  </Tooltip>,
                  <Popconfirm
                    title="确定删除此预设吗？"
                    onConfirm={() => handleDeletePreset(preset.id)}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Tooltip title="删除预设">
                      <DeleteOutlined style={{ color: '#ff4d4f' }} />
                    </Tooltip>
                  </Popconfirm>
                ]}
              >
                <div style={{ marginBottom: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong>{preset.name}</strong>
                    {preset.usage_count > 0 && (
                      <div style={{ display: 'flex', alignItems: 'center', fontSize: '12px', color: '#666' }}>
                        <StarOutlined style={{ marginRight: 2 }} />
                        {preset.usage_count}
                      </div>
                    )}
                  </div>
                </div>
                
                <p style={{ fontSize: '12px', color: '#666', marginBottom: 12 }}>
                  {preset.description}
                </p>
                
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                  <Tag color={getStyleColor(preset.style)} size="small">
                    {preset.style}
                  </Tag>
                  <Tag color={getDurationColor(preset.duration)} size="small">
                    {preset.duration}
                  </Tag>
                  <Tag color="blue" size="small">
                    {preset.template_id}
                  </Tag>
                  {preset.voice_config?.enabled && (
                    <Tag color="green" size="small">
                      语音
                    </Tag>
                  )}
                </div>
                
                {preset.updated_at && (
                  <div style={{ 
                    fontSize: '10px', 
                    color: '#999', 
                    marginTop: 8,
                    display: 'flex',
                    alignItems: 'center'
                  }}>
                    <ClockCircleOutlined style={{ marginRight: 4 }} />
                    {new Date(preset.updated_at).toLocaleDateString()}
                  </div>
                )}
              </Card>
            </Col>
          ))}
        </Row>
      )}

      <Modal
        title={editingPreset ? "编辑预设" : "保存预设"}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingPreset(null);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSavePreset}
          initialValues={{
            style: 'educational',
            duration: '30s'
          }}
        >
          <Form.Item
            label="预设名称"
            name="name"
            rules={[{ required: true, message: '请输入预设名称' }]}
          >
            <Input placeholder="例如：商务演示、教育科普" />
          </Form.Item>

          <Form.Item
            label="预设描述"
            name="description"
            rules={[{ required: true, message: '请输入预设描述' }]}
          >
            <TextArea 
              rows={3}
              placeholder="描述这个预设的用途和特点"
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="视频风格"
                name="style"
                rules={[{ required: true, message: '请选择视频风格' }]}
              >
                <Select>
                  <Option value="educational">教育科普</Option>
                  <Option value="entertainment">娱乐搞笑</Option>
                  <Option value="commercial">商业推广</Option>
                  <Option value="news">新闻资讯</Option>
                </Select>
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item
                label="视频时长"
                name="duration"
                rules={[{ required: true, message: '请选择视频时长' }]}
              >
                <Select>
                  <Option value="15s">15秒</Option>
                  <Option value="30s">30秒</Option>
                  <Option value="60s">60秒</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <Button onClick={() => {
                setModalVisible(false);
                setEditingPreset(null);
                form.resetFields();
              }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingPreset ? '更新' : '保存'}
              </Button>
            </div>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default PresetManager;