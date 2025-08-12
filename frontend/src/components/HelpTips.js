import React, { useState } from 'react';
import { Card, Collapse, Tag, Divider, Button, Modal } from 'antd';
import { QuestionCircleOutlined, BulbOutlined } from '@ant-design/icons';

const { Panel } = Collapse;

export const ScriptTips = () => {
  const tips = [
    {
      title: "主题选择技巧",
      content: [
        "选择具体而非宽泛的主题，如'Python 列表操作'而非'编程'",
        "考虑目标受众的知识水平和兴趣点",
        "热门话题更容易获得关注，但竞争也更激烈"
      ]
    },
    {
      title: "风格选择指南",
      content: [
        "教育科普：适合知识分享，语言严谨专业",
        "娱乐搞笑：适合轻松内容，语言活泼有趣",
        "商业推广：适合产品介绍，突出价值卖点",
        "新闻资讯：适合时事评论，客观中性表达"
      ]
    },
    {
      title: "时长建议",
      content: [
        "15秒：适合快速要点，抖音等平台首选",
        "30秒：平衡深度与关注度，最受欢迎",
        "60秒：深入讲解，适合复杂主题"
      ]
    }
  ];

  return (
    <Card 
      title={
        <span>
          <BulbOutlined style={{ color: '#faad14', marginRight: 8 }} />
          创作小贴士
        </span>
      }
      size="small"
      style={{ marginTop: 16 }}
    >
      <Collapse ghost size="small">
        {tips.map((tip, index) => (
          <Panel header={tip.title} key={index}>
            <ul style={{ margin: 0, paddingLeft: 16 }}>
              {tip.content.map((item, i) => (
                <li key={i} style={{ marginBottom: 4, fontSize: '12px', color: '#666' }}>
                  {item}
                </li>
              ))}
            </ul>
          </Panel>
        ))}
      </Collapse>
    </Card>
  );
};

export const TemplateTips = () => {
  return (
    <Card 
      title={
        <span>
          <BulbOutlined style={{ color: '#1890ff', marginRight: 8 }} />
          模板选择建议
        </span>
      }
      size="small"
      style={{ marginTop: 16 }}
    >
      <div style={{ fontSize: '12px', color: '#666' }}>
        <p><Tag color="blue">默认模板</Tag> 适合大多数内容，白色文字居中显示</p>
        <p><Tag color="green">现代简约</Tag> 适合商务内容，底部文字显示</p>
        <p><Tag color="cyan">科技风格</Tag> 适合技术内容，青色文字突出</p>
        <p><Tag color="orange">优雅风格</Tag> 适合生活内容，顶部文字显示</p>
      </div>
    </Card>
  );
};

export const VoiceTips = () => {
  return (
    <Card 
      title={
        <span>
          <QuestionCircleOutlined style={{ color: '#722ed1', marginRight: 8 }} />
          语音配置说明
        </span>
      }
      size="small"
      style={{ marginTop: 16 }}
    >
      <div style={{ fontSize: '12px', color: '#666' }}>
        <p><strong>Google TTS：</strong>免费使用，支持多种语言，音质良好</p>
        <p><strong>OpenAI TTS：</strong>需要 API 密钥，音质更佳，更自然</p>
        <Divider style={{ margin: '8px 0' }} />
        <p><strong>语速建议：</strong></p>
        <p>• 教育内容：0.8-1.0x（便于理解）</p>
        <p>• 娱乐内容：1.0-1.2x（保持节奏）</p>
        <p>• 新闻资讯：0.9-1.1x（清晰准确）</p>
      </div>
    </Card>
  );
};

export const HelpModal = ({ visible, onClose }) => {
  return (
    <Modal
      title="使用帮助"
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="close" type="primary" onClick={onClose}>
          知道了
        </Button>
      ]}
      width={600}
    >
      <div>
        <h4>🎬 制作流程</h4>
        <ol style={{ paddingLeft: 20 }}>
          <li>输入视频主题，选择风格和时长</li>
          <li>AI 自动生成视频脚本</li>
          <li>选择视频模板和语音配置</li>
          <li>制作并下载完成的视频</li>
        </ol>

        <Divider />

        <h4>💡 最佳实践</h4>
        <ul style={{ paddingLeft: 20 }}>
          <li>主题要具体明确，避免过于宽泛</li>
          <li>根据内容类型选择合适的风格</li>
          <li>30秒时长最受欢迎，平衡了内容深度和观看体验</li>
          <li>可以多次生成脚本，选择最满意的版本</li>
          <li>预览语音效果，确保符合内容调性</li>
        </ul>

        <Divider />

        <h4>🔧 技术说明</h4>
        <ul style={{ paddingLeft: 20 }}>
          <li>视频分辨率：1280x720 (HD)</li>
          <li>视频格式：MP4，兼容性最佳</li>
          <li>语音合成：支持中英文等多种语言</li>
          <li>素材来源：免费图片库，无版权问题</li>
        </ul>
      </div>
    </Modal>
  );
};