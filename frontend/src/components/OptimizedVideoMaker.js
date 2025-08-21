import React, { useState, useEffect } from 'react';
import './OptimizedVideoMaker.css';

const OptimizedVideoMaker = () => {
  const [videoTopic, setVideoTopic] = useState('旅游攻略分享');
  const [videoStyle, setVideoStyle] = useState('教育科普');
  const [videoDuration, setVideoDuration] = useState(30);
  const [isGenerating, setIsGenerating] = useState(false);
  const [suggestions, setSuggestions] = useState([
    '运动健身指南',
    '摄影技巧教学',
    'Python 编程入门',
    '美食制作教程',
    '生活小妙招'
  ]);

  const styleOptions = [
    { value: '教育科普', label: '教育科普', description: '知识分享、教程讲解', icon: '📚' },
    { value: '娱乐搞笑', label: '娱乐搞笑', description: '搞笑段子、生活趣事', icon: '😄' },
    { value: '商业推广', label: '商业推广', description: '产品介绍、品牌宣传', icon: '💼' },
    { value: '生活记录', label: '生活记录', description: '日常分享、生活感悟', icon: '📱' }
  ];

  const durationOptions = [
    { value: 15, label: '15秒', description: '简洁明了，快速传达' },
    { value: 30, label: '30秒', description: '平衡深度，最受欢迎' },
    { value: 60, label: '60秒', description: '详细讲解，深度内容' },
    { value: 90, label: '90秒', description: '完整故事，沉浸体验' }
  ];

  const handleGenerateScript = async () => {
    setIsGenerating(true);
    // 模拟生成过程
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsGenerating(false);
    // 这里可以添加实际的脚本生成逻辑
  };

  const handleSuggestionClick = (suggestion) => {
    setVideoTopic(suggestion);
  };

  const refreshSuggestions = () => {
    const newSuggestions = [
      '健康饮食指南',
      '旅行摄影技巧',
      '职场沟通技巧',
      '家居收纳妙招',
      '宠物护理知识'
    ];
    setSuggestions(newSuggestions);
  };

  return (
    <div className="video-maker-container">
      {/* 主内容区域 */}
      <div className="main-content">
        <div className="content-header">
          <h1 className="page-title">AI 短视频制作</h1>
          <p className="page-subtitle">让创意更简单，让内容更精彩</p>
        </div>

        <div className="input-section">
          {/* 视频主题输入 */}
          <div className="input-group topic-input">
            <label className="input-label">
              <span className="label-icon">🎯</span>
              视频主题
            </label>
            <input
              type="text"
              value={videoTopic}
              onChange={(e) => setVideoTopic(e.target.value)}
              placeholder="输入您想要制作的视频主题..."
              className="topic-input-field"
            />
            <div className="input-hint">建议使用具体、描述性的主题</div>
          </div>

          {/* 风格和时长选择 */}
          <div className="selection-row">
            <div className="input-group style-selector">
              <label className="input-label">
                <span className="label-icon">🎨</span>
                视频风格
              </label>
              <div className="style-options">
                {styleOptions.map((style) => (
                  <div
                    key={style.value}
                    className={`style-option ${videoStyle === style.value ? 'selected' : ''}`}
                    onClick={() => setVideoStyle(style.value)}
                  >
                    <span className="style-icon">{style.icon}</span>
                    <div className="style-info">
                      <div className="style-label">{style.label}</div>
                      <div className="style-description">{style.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="input-group duration-selector">
              <label className="input-label">
                <span className="label-icon">⏱️</span>
                视频时长
              </label>
              <div className="duration-options">
                {durationOptions.map((duration) => (
                  <div
                    key={duration.value}
                    className={`duration-option ${videoDuration === duration.value ? 'selected' : ''}`}
                    onClick={() => setVideoDuration(duration.value)}
                  >
                    <div className="duration-value">{duration.label}</div>
                    <div className="duration-description">{duration.description}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 生成按钮 */}
          <div className="action-section">
            <button
              className={`generate-button ${isGenerating ? 'generating' : ''}`}
              onClick={handleGenerateScript}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <span className="loading-spinner"></span>
                  正在生成中...
                </>
              ) : (
                <>
                  <span className="button-icon">✨</span>
                  生成脚本
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* 右侧边栏 */}
      <div className="sidebar">
        {/* 主题建议 */}
        <div className="sidebar-section">
          <div className="section-header">
            <span className="section-icon">💡</span>
            <h3>主题建议</h3>
          </div>
          <p className="section-hint">点击下方主题快速填入</p>
          <div className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                className="suggestion-item"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
          <button className="refresh-button" onClick={refreshSuggestions}>
            🔄 换一批建议
          </button>
        </div>

        {/* 脚本模板 */}
        <div className="sidebar-section">
          <div className="section-header">
            <span className="section-icon">📋</span>
            <h3>脚本模板</h3>
          </div>
          <div className="template-categories">
            {styleOptions.map((style) => (
              <div key={style.value} className="template-category">
                <div className="category-header">
                  <span className="category-icon">{style.icon}</span>
                  <span className="category-name">{style.label}</span>
                </div>
                <p className="category-description">{style.description}</p>
                <div className="template-example">
                  示例: {style.value === '教育科普' ? 'Python 编程入门' : 
                         style.value === '娱乐搞笑' ? '程序员的日常' : 
                         style.value === '商业推广' ? '新产品发布' : '生活感悟分享'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 创作小贴士 */}
        <div className="sidebar-section">
          <div className="section-header">
            <span className="section-icon">💡</span>
            <h3>创作小贴士</h3>
          </div>
          <div className="tips-list">
            <div className="tip-item">
              <span className="tip-arrow">→</span>
              主题选择技巧
            </div>
            <div className="tip-item">
              <span className="tip-arrow">→</span>
              风格选择指南
            </div>
            <div className="tip-item">
              <span className="tip-arrow">→</span>
              时长建议
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OptimizedVideoMaker;
