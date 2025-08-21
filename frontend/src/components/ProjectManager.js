import React, { useState, useEffect } from 'react';
import { 
  Card, 
  List, 
  Button, 
  Modal, 
  Input, 
  message, 
  Popconfirm,
  Tag,
  Space,
  Row,
  Col,
  Avatar,
  Tooltip,
  Select,
  DatePicker
} from 'antd';
import { 
  FolderOutlined,
  SaveOutlined,
  DeleteOutlined,
  EditOutlined,
  PlayCircleOutlined,
  CopyOutlined,
  ExportOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import api from '../utils/api';
import { t } from '../utils/i18n';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Option } = Select;

function ProjectManager({ 
  currentProject, 
  onProjectLoad, 
  onProjectSave,
  script,
  videoConfig 
}) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [currentEditProject, setCurrentEditProject] = useState(null);
  const [projectForm, setProjectForm] = useState({
    name: '',
    description: '',
    tags: [],
    category: 'general'
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [sortBy, setSortBy] = useState('updated_time');

  const categories = [
    { value: 'general', label: '通用', color: 'blue' },
    { value: 'education', label: '教育', color: 'green' },
    { value: 'marketing', label: '营销', color: 'orange' },
    { value: 'entertainment', label: '娱乐', color: 'purple' },
    { value: 'news', label: '新闻', color: 'red' },
    { value: 'tutorial', label: '教程', color: 'cyan' }
  ];

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await api.get('/projects/list');
      setProjects(data.projects || []);
    } catch (error) {
      console.error('加载项目失败:', error);
      message.error('加载项目列表失败');
    } finally {
      setLoading(false);
    }
  };

  const saveProject = async () => {
    if (!projectForm.name.trim()) {
      message.error('请输入项目名称');
      return;
    }

    if (!script) {
      message.error('没有可保存的脚本内容');
      return;
    }

    try {
      const projectData = {
        name: projectForm.name,
        description: projectForm.description,
        category: projectForm.category,
        tags: projectForm.tags,
        script: script,
        video_config: videoConfig || {},
        thumbnail: generateThumbnail(),
        created_time: new Date().toISOString(),
        updated_time: new Date().toISOString()
      };

      const response = await api.post('/projects/save', projectData);
      
      message.success('项目保存成功');
      setSaveModalVisible(false);
      setProjectForm({ name: '', description: '', tags: [], category: 'general' });
      loadProjects();
      
      // 通知父组件
      onProjectSave && onProjectSave(response.project);
      
    } catch (error) {
      console.error('保存项目失败:', error);
      message.error('保存项目失败');
    }
  };

  const loadProject = async (project) => {
    try {
      const data = await api.get(`/projects/${project.id}`);
      const projectData = data.project;
      
      message.success(`已加载项目：${projectData.name}`);
      
      // 通知父组件加载项目
      onProjectLoad && onProjectLoad(projectData);
      
    } catch (error) {
      console.error('加载项目失败:', error);
      message.error('加载项目失败');
    }
  };

  const deleteProject = async (projectId) => {
    try {
      await api.delete(`/projects/${projectId}`);
      message.success('项目删除成功');
      loadProjects();
    } catch (error) {
      console.error('删除项目失败:', error);
      message.error('删除项目失败');
    }
  };

  const duplicateProject = async (project) => {
    try {
      const duplicateData = {
        ...project,
        name: `${project.name} - 副本`,
        id: undefined,
        created_time: new Date().toISOString(),
        updated_time: new Date().toISOString()
      };
      
      await api.post('/projects/save', duplicateData);
      message.success('项目复制成功');
      loadProjects();
    } catch (error) {
      console.error('复制项目失败:', error);
      message.error('复制项目失败');
    }
  };

  const updateProject = async () => {
    if (!currentEditProject || !projectForm.name.trim()) {
      message.error('请输入项目名称');
      return;
    }

    try {
      const updateData = {
        name: projectForm.name,
        description: projectForm.description,
        category: projectForm.category,
        tags: projectForm.tags,
        updated_time: new Date().toISOString()
      };

      await api.put(`/projects/${currentEditProject.id}`, updateData);
      
      message.success('项目信息更新成功');
      setEditModalVisible(false);
      setCurrentEditProject(null);
      setProjectForm({ name: '', description: '', tags: [], category: 'general' });
      loadProjects();
      
    } catch (error) {
      console.error('更新项目失败:', error);
      message.error('更新项目失败');
    }
  };

  const generateThumbnail = () => {
    // 生成项目缩略图（基于脚本内容）
    if (script && script.scenes && script.scenes.length > 0) {
      return {
        scene_count: script.scenes.length,
        first_scene_text: script.scenes[0].text?.substring(0, 50) + '...',
        total_duration: script.total_duration || 0
      };
    }
    return null;
  };

  const openSaveModal = () => {
    setProjectForm({
      name: currentProject?.name || '',
      description: currentProject?.description || '',
      tags: currentProject?.tags || [],
      category: currentProject?.category || 'general'
    });
    setSaveModalVisible(true);
  };

  const openEditModal = (project) => {
    setCurrentEditProject(project);
    setProjectForm({
      name: project.name,
      description: project.description || '',
      tags: project.tags || [],
      category: project.category || 'general'
    });
    setEditModalVisible(true);
  };

  const filteredProjects = projects
    .filter(project => {
      const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (project.description || '').toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = filterCategory === 'all' || project.category === filterCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'created_time':
          return new Date(b.created_time) - new Date(a.created_time);
        case 'updated_time':
        default:
          return new Date(b.updated_time) - new Date(a.updated_time);
      }
    });

  const getCategoryInfo = (category) => {
    return categories.find(cat => cat.value === category) || categories[0];
  };

  const formatDate = (dateString) => {
    return dayjs(dateString).format('YYYY-MM-DD HH:mm');
  };

  const getProjectStats = () => {
    const totalProjects = projects.length;
    const categoryCounts = {};
    projects.forEach(project => {
      const category = project.category || 'general';
      categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    });
    
    return { totalProjects, categoryCounts };
  };

  const stats = getProjectStats();

  return (
    <div className="project-manager">
      {/* 项目统计 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={[16, 8]}>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: '#1890ff' }}>
                {stats.totalProjects}
              </div>
              <div style={{ color: '#666', fontSize: 12 }}>总项目数</div>
            </div>
          </Col>
          <Col span={18}>
            <div>
              <div style={{ marginBottom: 4, fontSize: 12, color: '#666' }}>分类分布:</div>
              <Space wrap>
                {Object.entries(stats.categoryCounts).map(([category, count]) => {
                  const categoryInfo = getCategoryInfo(category);
                  return (
                    <Tag key={category} color={categoryInfo.color} size="small">
                      {categoryInfo.label}: {count}
                    </Tag>
                  );
                })}
              </Space>
            </div>
          </Col>
        </Row>
      </Card>

      {/* 操作栏 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={[8, 8]} align="middle">
          <Col span={6}>
            <Button 
              type="primary" 
              icon={<SaveOutlined />}
              onClick={openSaveModal}
              disabled={!script}
            >
              保存项目
            </Button>
          </Col>
          <Col span={6}>
            <Input.Search
              placeholder={t('project.search.placeholder', '搜索项目...')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              size="small"
            />
          </Col>
          <Col span={6}>
            <Select
              value={filterCategory}
              onChange={setFilterCategory}
              size="small"
              style={{ width: '100%' }}
            >
              <Option value="all">所有分类</Option>
              {categories.map(cat => (
                <Option key={cat.value} value={cat.value}>
                  {cat.label}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={6}>
            <Select
              value={sortBy}
              onChange={setSortBy}
              size="small"
              style={{ width: '100%' }}
            >
              <Option value="updated_time">最近更新</Option>
              <Option value="created_time">创建时间</Option>
              <Option value="name">项目名称</Option>
            </Select>
          </Col>
        </Row>
      </Card>

      {/* 项目列表 */}
      <Card title={`项目列表 (${filteredProjects.length})`}>
        <List
          loading={loading}
          dataSource={filteredProjects}
          renderItem={(project) => {
            const categoryInfo = getCategoryInfo(project.category);
            return (
              <List.Item
                actions={[
                  <Tooltip title="加载项目">
                    <Button
                      type="text"
                      icon={<FolderOutlined />}
                      onClick={() => loadProject(project)}
                    />
                  </Tooltip>,
                  <Tooltip title="编辑信息">
                    <Button
                      type="text"
                      icon={<EditOutlined />}
                      onClick={() => openEditModal(project)}
                    />
                  </Tooltip>,
                  <Tooltip title="复制项目">
                    <Button
                      type="text"
                      icon={<CopyOutlined />}
                      onClick={() => duplicateProject(project)}
                    />
                  </Tooltip>,
                  <Popconfirm
                    title="确定删除这个项目吗？"
                    onConfirm={() => deleteProject(project.id)}
                  >
                    <Tooltip title="删除项目">
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                      />
                    </Tooltip>
                  </Popconfirm>
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <Avatar 
                      style={{ 
                        backgroundColor: `var(--ant-color-${categoryInfo.color})`,
                        color: 'white'
                      }}
                      icon={<FileTextOutlined />}
                    />
                  }
                  title={
                    <div>
                      <span style={{ marginRight: 8 }}>{project.name}</span>
                      <Tag color={categoryInfo.color} size="small">
                        {categoryInfo.label}
                      </Tag>
                      {project.tags && project.tags.map(tag => (
                        <Tag key={tag} size="small" style={{ marginLeft: 4 }}>
                          {tag}
                        </Tag>
                      ))}
                    </div>
                  }
                  description={
                    <div>
                      <div style={{ marginBottom: 4 }}>
                        {project.description || '暂无描述'}
                      </div>
                      <div style={{ fontSize: 12, color: '#999' }}>
                        <Space split={<span>•</span>}>
                          <span>
                            <CalendarOutlined style={{ marginRight: 4 }} />
                            创建: {formatDate(project.created_time)}
                          </span>
                          <span>
                            <ClockCircleOutlined style={{ marginRight: 4 }} />
                            更新: {formatDate(project.updated_time)}
                          </span>
                          {project.thumbnail && (
                            <span>
                              场景: {project.thumbnail.scene_count}个
                            </span>
                          )}
                        </Space>
                      </div>
                    </div>
                  }
                />
              </List.Item>
            );
          }}
        />
      </Card>

      {/* 保存项目模态框 */}
      <Modal
        title="保存项目"
        open={saveModalVisible}
        onOk={saveProject}
        onCancel={() => setSaveModalVisible(false)}
        okText="保存"
        cancelText="取消"
      >
        <div style={{ marginBottom: 16 }}>
          <label>项目名称 *</label>
          <Input
            value={projectForm.name}
            onChange={(e) => setProjectForm(prev => ({ ...prev, name: e.target.value }))}
            placeholder="输入项目名称"
            style={{ marginTop: 4 }}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label>项目描述</label>
          <TextArea
            value={projectForm.description}
            onChange={(e) => setProjectForm(prev => ({ ...prev, description: e.target.value }))}
            placeholder="输入项目描述"
            rows={3}
            style={{ marginTop: 4 }}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label>项目分类</label>
          <Select
            value={projectForm.category}
            onChange={(value) => setProjectForm(prev => ({ ...prev, category: value }))}
            style={{ width: '100%', marginTop: 4 }}
          >
            {categories.map(cat => (
              <Option key={cat.value} value={cat.value}>
                <Tag color={cat.color} size="small" style={{ marginRight: 8 }}>
                  {cat.label}
                </Tag>
              </Option>
            ))}
          </Select>
        </div>

        <div>
          <label>标签</label>
          <Select
            mode="tags"
            value={projectForm.tags}
            onChange={(value) => setProjectForm(prev => ({ ...prev, tags: value }))}
            placeholder="添加标签"
            style={{ width: '100%', marginTop: 4 }}
          />
        </div>
      </Modal>

      {/* 编辑项目模态框 */}
      <Modal
        title="编辑项目信息"
        open={editModalVisible}
        onOk={updateProject}
        onCancel={() => setEditModalVisible(false)}
        okText="更新"
        cancelText="取消"
      >
        <div style={{ marginBottom: 16 }}>
          <label>项目名称 *</label>
          <Input
            value={projectForm.name}
            onChange={(e) => setProjectForm(prev => ({ ...prev, name: e.target.value }))}
            placeholder="输入项目名称"
            style={{ marginTop: 4 }}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label>项目描述</label>
          <TextArea
            value={projectForm.description}
            onChange={(e) => setProjectForm(prev => ({ ...prev, description: e.target.value }))}
            placeholder="输入项目描述"
            rows={3}
            style={{ marginTop: 4 }}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label>项目分类</label>
          <Select
            value={projectForm.category}
            onChange={(value) => setProjectForm(prev => ({ ...prev, category: value }))}
            style={{ width: '100%', marginTop: 4 }}
          >
            {categories.map(cat => (
              <Option key={cat.value} value={cat.value}>
                <Tag color={cat.color} size="small" style={{ marginRight: 8 }}>
                  {cat.label}
                </Tag>
              </Option>
            ))}
          </Select>
        </div>

        <div>
          <label>标签</label>
          <Select
            mode="tags"
            value={projectForm.tags}
            onChange={(value) => setProjectForm(prev => ({ ...prev, tags: value }))}
            placeholder="添加标签"
            style={{ width: '100%', marginTop: 4 }}
          />
        </div>
      </Modal>
    </div>
  );
}

export default ProjectManager;