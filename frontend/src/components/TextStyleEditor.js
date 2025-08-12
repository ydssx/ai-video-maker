import React, { useState } from 'react';
import { Card, Row, Col, Select, Slider, ColorPicker, Switch, Radio, Divider } from 'antd';
import { FontSizeOutlined, BgColorsOutlined, AlignLeftOutlined, AlignCenterOutlined, AlignRightOutlined } from '@ant-design/icons';

const { Option } = Select;

function TextStyleEditor({ textStyle, onStyleChange }) {
  const [style, setStyle] = useState({
    fontFamily: 'Arial',
    fontSize: 48,
    fontColor: '#ffffff',
    strokeColor: '#000000',
    strokeWidth: 2,
    backgroundColor: 'transparent',
    backgroundOpacity: 0,
    position: 'center',
    animation: 'fade_in',
    shadow: true,
    shadowColor: '#000000',
    shadowOffset: 2,
    ...textStyle
  });

  const handleStyleChange = (key, value) => {
    const newStyle = { ...style, [key]: value };
    setStyle(newStyle);
    onStyleChange(newStyle);
  };

  const fontFamilies = [
    { value: 'Arial', label: 'Arial' },
    { value: 'Microsoft YaHei', label: '微软雅黑' },
    { value: 'SimHei', label: '黑体' },
    { value: 'SimSun', label: '宋体' },
    { value: 'KaiTi', label: '楷体' },
    { value: 'Times New Roman', label: 'Times New Roman' },
    { value: 'Helvetica', label: 'Helvetica' },
    { value: 'Georgia', label: 'Georgia' }
  ];

  const animations = [
    { value: 'fade_in', label: '淡入' },
    { value: 'slide_up', label: '上滑' },
    { value: 'slide_down', label: '下滑' },
    { value: 'slide_left', label: '左滑' },
    { value: 'slide_right', label: '右滑' },
    { value: 'zoom_in', label: '缩放进入' },
    { value: 'bounce_in', label: '弹跳进入' },
    { value: 'typewriter', label: '打字机效果' }
  ];

  return (
    <Card title="文字样式编辑" size="small">
      <Row gutter={[16, 16]}>
        {/* 字体设置 */}
        <Col span={24}>
          <div style={{ marginBottom: 8 }}>
            <FontSizeOutlined style={{ marginRight: 8 }} />
            字体设置
          </div>
        </Col>
        
        <Col span={12}>
          <div style={{ marginBottom: 4 }}>字体</div>
          <Select
            value={style.fontFamily}
            onChange={(value) => handleStyleChange('fontFamily', value)}
            style={{ width: '100%' }}
          >
            {fontFamilies.map(font => (
              <Option key={font.value} value={font.value}>
                <span style={{ fontFamily: font.value }}>{font.label}</span>
              </Option>
            ))}
          </Select>
        </Col>

        <Col span={12}>
          <div style={{ marginBottom: 4 }}>字体大小</div>
          <Slider
            min={20}
            max={100}
            value={style.fontSize}
            onChange={(value) => handleStyleChange('fontSize', value)}
            marks={{
              20: '小',
              50: '中',
              100: '大'
            }}
          />
        </Col>

        <Divider style={{ margin: '12px 0' }} />

        {/* 颜色设置 */}
        <Col span={24}>
          <div style={{ marginBottom: 8 }}>
            <BgColorsOutlined style={{ marginRight: 8 }} />
            颜色设置
          </div>
        </Col>

        <Col span={8}>
          <div style={{ marginBottom: 4 }}>文字颜色</div>
          <ColorPicker
            value={style.fontColor}
            onChange={(color) => handleStyleChange('fontColor', color.toHexString())}
            showText
          />
        </Col>

        <Col span={8}>
          <div style={{ marginBottom: 4 }}>描边颜色</div>
          <ColorPicker
            value={style.strokeColor}
            onChange={(color) => handleStyleChange('strokeColor', color.toHexString())}
            showText
          />
        </Col>

        <Col span={8}>
          <div style={{ marginBottom: 4 }}>描边宽度</div>
          <Slider
            min={0}
            max={10}
            value={style.strokeWidth}
            onChange={(value) => handleStyleChange('strokeWidth', value)}
          />
        </Col>

        <Divider style={{ margin: '12px 0' }} />

        {/* 位置设置 */}
        <Col span={24}>
          <div style={{ marginBottom: 8 }}>文字位置</div>
          <Radio.Group
            value={style.position}
            onChange={(e) => handleStyleChange('position', e.target.value)}
            buttonStyle="solid"
          >
            <Radio.Button value="top">
              <AlignLeftOutlined style={{ transform: 'rotate(90deg)' }} />
              顶部
            </Radio.Button>
            <Radio.Button value="center">
              <AlignCenterOutlined />
              居中
            </Radio.Button>
            <Radio.Button value="bottom">
              <AlignRightOutlined style={{ transform: 'rotate(90deg)' }} />
              底部
            </Radio.Button>
          </Radio.Group>
        </Col>

        <Divider style={{ margin: '12px 0' }} />

        {/* 动画效果 */}
        <Col span={24}>
          <div style={{ marginBottom: 8 }}>动画效果</div>
          <Select
            value={style.animation}
            onChange={(value) => handleStyleChange('animation', value)}
            style={{ width: '100%' }}
          >
            {animations.map(anim => (
              <Option key={anim.value} value={anim.value}>
                {anim.label}
              </Option>
            ))}
          </Select>
        </Col>

        <Divider style={{ margin: '12px 0' }} />

        {/* 阴影设置 */}
        <Col span={24}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <Switch
              checked={style.shadow}
              onChange={(checked) => handleStyleChange('shadow', checked)}
              style={{ marginRight: 8 }}
            />
            文字阴影
          </div>
        </Col>

        {style.shadow && (
          <>
            <Col span={12}>
              <div style={{ marginBottom: 4 }}>阴影颜色</div>
              <ColorPicker
                value={style.shadowColor}
                onChange={(color) => handleStyleChange('shadowColor', color.toHexString())}
                showText
              />
            </Col>

            <Col span={12}>
              <div style={{ marginBottom: 4 }}>阴影偏移</div>
              <Slider
                min={0}
                max={10}
                value={style.shadowOffset}
                onChange={(value) => handleStyleChange('shadowOffset', value)}
              />
            </Col>
          </>
        )}

        <Divider style={{ margin: '12px 0' }} />

        {/* 预览 */}
        <Col span={24}>
          <div style={{ marginBottom: 8 }}>预览效果</div>
          <div
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              padding: '40px',
              borderRadius: '8px',
              textAlign: style.position === 'center' ? 'center' : 
                        style.position === 'top' ? 'center' : 'center',
              display: 'flex',
              alignItems: style.position === 'center' ? 'center' : 
                         style.position === 'top' ? 'flex-start' : 'flex-end',
              justifyContent: 'center',
              minHeight: '120px'
            }}
          >
            <span
              style={{
                fontFamily: style.fontFamily,
                fontSize: `${style.fontSize * 0.5}px`, // 缩放预览
                color: style.fontColor,
                textShadow: style.shadow ? 
                  `${style.shadowOffset}px ${style.shadowOffset}px 0px ${style.shadowColor}` : 'none',
                WebkitTextStroke: `${style.strokeWidth}px ${style.strokeColor}`,
                fontWeight: 'bold'
              }}
            >
              示例文字
            </span>
          </div>
        </Col>
      </Row>
    </Card>
  );
}

export default TextStyleEditor;