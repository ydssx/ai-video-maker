import React, { useState, useEffect } from 'react';
import {
  Card,
  Upload,
  Button,
  Row,
  Col,
  Image,
  Tag,
  Modal,
  Input,
  Select,
  message,
  Popconfirm,
  Empty,
  Tabs
} from 'antd';
import {
  UploadOutlined,
  DeleteOutlined,
  EyeOutlined,
  EditOutlined,
  PictureOutlined,
  VideoCameraOutlined,
  SoundOutlined
} from '@ant-design/icons';

const { TabPane } = Tabs;
const { Search } = Input;
const { Option } = Select;

function AssetManager({ onAssetSelect }) {
  const [assets, setAssets] = useState({
    images: [],
    videos: [],
    audio: []
  });
  const [loading, setLoading] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewAsset, setPreviewAsset] = useState(null);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeTab, setActiveTab] = useState('images');

  useEffect(() => {
    loadAssets();
  }, []);

  const loadAssets = async () => {
    setLoading(true);
    try {
      // 这里应该从后端加载用户上传的素材
      // const response = await axios.get('/api/assets/user-assets');
      // setAssets(response.data);

      // 模拟数据
      setAssets({
        images: [
          {
            id: '1',
            name: '示例图片1.jpg',
            url: 'https://picsum.photos/800/600?random=1',
            thumb: 'https://picsum.photos/200/150?random=1',
            type: 'image',
            size: '2.5MB',
            uploadTime: '2024-01-15',
            tags: ['风景', '自然']
          },
          {
            id: '2',
            name: '示例图片2.jpg',
            url: 'https://picsum.photos/800/600?random=2',
            thumb: 'https://picsum.photos/200/150?random=2',
            type: 'image',
            size: '1.8MB',
            uploadTime: '2024-01-14',
            tags: ['城市', '建筑']
          }
        ],
        videos: [],
        audio: []
      });
    } catch (error) {
      console.error('加载素材失败:', error);
      message.error('加载素材失败');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file, type) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    try {
      // 这里应该上传到后端
      // const response = await axios.post('/api/assets/upload', formData);

      // 模拟上传成功
      const newAsset = {
        id: Date.now().toString(),
        name: file.name,
        url: URL.createObjectURL(file),
        thumb: URL.createObjectURL(file),
        type: type,
        size: `${(file.size / 1024 / 1024).toFixed(1)}MB`,
        uploadTime: new Date().toISOString().split('T')[0],
        tags: []
      };

      setAssets(prev => ({
        ...prev,
        [type === 'image' ? 'images' : type === 'video' ? 'videos' : 'audio']: [
          ...prev[type === 'image' ? 'images' : type === 'video' ? 'videos' : 'audio'],
          newAsset
        ]
      }));

      message.success('上传成功');
    } catch (error) {
      console.error('上传失败:', error);
      message.error('上传失败');
    }

    return false; // 阻止默认上传行为
  };

  const handleDeleteAsset = async (assetId, type) => {
    try {
      // 这里应该从后端删除
      // await axios.delete(`/api/assets/${assetId}`);

      setAssets(prev => ({
        ...prev,
        [type]: prev[type].filter(asset => asset.id !== assetId)
      }));

      message.success('删除成功');
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  const handlePreview = (asset) => {
    setPreviewAsset(asset);
    setPreviewVisible(true);
  };

  const getFilteredAssets = (assetType) => {
    let filtered = assets[assetType] || [];

    if (searchKeyword) {
      filtered = filtered.filter(asset =>
        asset.name.toLowerCase().includes(searchKeyword.toLowerCase()) ||
        asset.tags.some(tag => tag.toLowerCase().includes(searchKeyword.toLowerCase()))
      );
    }

    return filtered;
  };

  const renderAssetCard = (asset, type) => (
    <Col span={6} key={asset.id}>
      <Card
        hoverable
        size="small"
        cover={
          type === 'images' ? (
            <div style={{ height: 120, overflow: 'hidden' }}>
              <img
                src={asset.thumb}
                alt={asset.name}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            </div>
          ) : type === 'videos' ? (
            <div style={{
              height: 120,
              background: '#f0f0f0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <VideoCameraOutlined style={{ fontSize: 32, color: '#999' }} />
            </div>
          ) : (
            <div style={{
              height: 120,
              background: '#f0f0f0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <SoundOutlined style={{ fontSize: 32, color: '#999' }} />
            </div>
          )
        }
        actions={[
          <EyeOutlined key="preview" onClick={() => handlePreview(asset)} />,
          <EditOutlined key="edit" onClick={() => onAssetSelect(asset)} />,
          <Popconfirm
            title="确定删除此素材吗？"
            onConfirm={() => handleDeleteAsset(asset.id, type)}
            okText="确定"
            cancelText="取消"
          >
            <DeleteOutlined key="delete" style={{ color: '#ff4d4f' }} />
          </Popconfirm>
        ]}
      >
        <Card.Meta
          title={
            <div style={{
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              fontSize: '12px'
            }}>
              {asset.name}
            </div>
          }
          description={
            <div>
              <div style={{ fontSize: '10px', color: '#999', marginBottom: 4 }}>
                {asset.size} • {asset.uploadTime}
              </div>
              <div>
                {asset.tags.map(tag => (
                  <Tag key={tag} size="small" color="blue">
                    {tag}
                  </Tag>
                ))}
              </div>
            </div>
          }
        />
      </Card>
    </Col>
  );

  const uploadProps = {
    beforeUpload: (file) => {
      const isValidType = file.type.startsWith('image/') ||
        file.type.startsWith('video/') ||
        file.type.startsWith('audio/');

      if (!isValidType) {
        message.error('只支持图片、视频和音频文件');
        return false;
      }

      const isLt50M = file.size / 1024 / 1024 < 50;
      if (!isLt50M) {
        message.error('文件大小不能超过 50MB');
        return false;
      }

      let type = 'image';
      if (file.type.startsWith('video/')) type = 'video';
      if (file.type.startsWith('audio/')) type = 'audio';

      return handleUpload(file, type);
    },
    showUploadList: false,
    multiple: true
  };

  return (
    <div>
      <Card title="素材管理" size="small">
        <div style={{ marginBottom: 16 }}>
          <Row gutter={16} align="middle">
            <Col span={8}>
              <Upload {...uploadProps}>
                <Button icon={<UploadOutlined />} type="primary">
                  上传素材
                </Button>
              </Upload>
            </Col>
            <Col span={8}>
              <Search
                placeholder="搜索素材..."
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                allowClear
              />
            </Col>
            <Col span={8}>
              <Select
                value={selectedCategory}
                onChange={setSelectedCategory}
                style={{ width: '100%' }}
                placeholder="选择分类"
              >
                <Option value="all">全部分类</Option>
                <Option value="nature">自然风景</Option>
                <Option value="business">商务办公</Option>
                <Option value="people">人物肖像</Option>
                <Option value="technology">科技数码</Option>
              </Select>
            </Col>
          </Row>
        </div>

        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane
            tab={
              <span>
                <PictureOutlined />
                图片 ({assets.images.length})
              </span>
            }
            key="images"
          >
            {getFilteredAssets('images').length > 0 ? (
              <Row gutter={[16, 16]}>
                {getFilteredAssets('images').map(asset =>
                  renderAssetCard(asset, 'images')
                )}
              </Row>
            ) : (
              <Empty description="暂无图片素材" />
            )}
          </TabPane>

          <TabPane
            tab={
              <span>
                <VideoCameraOutlined />
                视频 ({assets.videos.length})
              </span>
            }
            key="videos"
          >
            {getFilteredAssets('videos').length > 0 ? (
              <Row gutter={[16, 16]}>
                {getFilteredAssets('videos').map(asset =>
                  renderAssetCard(asset, 'videos')
                )}
              </Row>
            ) : (
              <Empty description="暂无视频素材" />
            )}
          </TabPane>

          <TabPane
            tab={
              <span>
                <SoundOutlined />
                音频 ({assets.audio.length})
              </span>
            }
            key="audio"
          >
            {getFilteredAssets('audio').length > 0 ? (
              <Row gutter={[16, 16]}>
                {getFilteredAssets('audio').map(asset =>
                  renderAssetCard(asset, 'audio')
                )}
              </Row>
            ) : (
              <Empty description="暂无音频素材" />
            )}
          </TabPane>
        </Tabs>
      </Card>

      <Modal
        open={previewVisible}
        title="素材预览"
        footer={null}
        onCancel={() => setPreviewVisible(false)}
        width={800}
      >
        {previewAsset && (
          <div style={{ textAlign: 'center' }}>
            {previewAsset.type === 'image' ? (
              <Image
                src={previewAsset.url}
                alt={previewAsset.name}
                style={{ maxWidth: '100%' }}
              />
            ) : previewAsset.type === 'video' ? (
              <video
                src={previewAsset.url}
                controls
                style={{ maxWidth: '100%', maxHeight: '400px' }}
              />
            ) : (
              <audio
                src={previewAsset.url}
                controls
                style={{ width: '100%' }}
              />
            )}

            <div style={{ marginTop: 16, textAlign: 'left' }}>
              <p><strong>文件名：</strong>{previewAsset.name}</p>
              <p><strong>大小：</strong>{previewAsset.size}</p>
              <p><strong>上传时间：</strong>{previewAsset.uploadTime}</p>
              <p><strong>标签：</strong>
                {previewAsset.tags.map(tag => (
                  <Tag key={tag} color="blue">{tag}</Tag>
                ))}
              </p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

export default AssetManager;