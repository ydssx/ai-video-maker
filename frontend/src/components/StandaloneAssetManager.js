import React from 'react';
import { Card, Tabs } from 'antd';
import { 
  FileImageOutlined, 
  SoundOutlined, 
  FolderOutlined 
} from '@ant-design/icons';
import AssetManager from './AssetManager';
import AudioManager from './AudioManager';
import ProjectManager from './ProjectManager';

const { TabPane } = Tabs;

function StandaloneAssetManager() {
  const handleAssetSelect = (asset) => {
    console.log('选择素材:', asset);
  };

  const handleAudioConfigChange = (config) => {
    console.log('音频配置变化:', config);
  };

  const handleProjectLoad = (project) => {
    console.log('加载项目:', project);
  };

  const handleProjectSave = (project) => {
    console.log('保存项目:', project);
  };

  return (
    <div className="standalone-asset-manager">
      <Card title="资源管理中心">
        <Tabs defaultActiveKey="assets" type="card">
          <TabPane
            tab={
              <span>
                <FileImageOutlined />
                素材库
              </span>
            }
            key="assets"
          >
            <AssetManager onAssetSelect={handleAssetSelect} />
          </TabPane>

          <TabPane
            tab={
              <span>
                <SoundOutlined />
                音频管理
              </span>
            }
            key="audio"
          >
            <AudioManager onAudioConfigChange={handleAudioConfigChange} />
          </TabPane>

          <TabPane
            tab={
              <span>
                <FolderOutlined />
                项目管理
              </span>
            }
            key="projects"
          >
            <ProjectManager
              onProjectLoad={handleProjectLoad}
              onProjectSave={handleProjectSave}
              script={null}
              videoConfig={{}}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
}

export default StandaloneAssetManager;