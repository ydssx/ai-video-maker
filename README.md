# AI 短视频制作平台

一个基于 AI 的智能短视频制作平台，支持脚本生成、语音合成、视频编辑等功能。

## 功能特性

### � 核心专功能
- **AI 脚本生成**: 基于主题自动生成视频脚本
- **智能语音合成**: 支持多种语音引擎和语言
- **模板系统**: 丰富的视频模板库
- **实时预览**: 所见即所得的视频预览

### 🎨 高级编辑
- **文字样式编辑**: 自定义字体、颜色、位置、动画
- **时间轴编辑**: 精确控制场景时间和播放
- **素材管理**: 上传和管理图片、视频、音频素材
- **音频管理**: 背景音乐和音效管理
- **转场效果**: 多种场景转场动画
- **导出设置**: 自定义视频质量和格式

### 📁 项目管理
- **项目保存**: 保存和管理视频项目
- **项目分类**: 按类别组织项目
- **标签系统**: 为项目添加标签便于搜索
- **项目复制**: 快速复制现有项目
- **导入导出**: 项目数据的导入导出

### 📊 数据统计
- **使用统计**: 视频制作数量和时长统计
- **项目分析**: 项目分类和标签分析
- **性能监控**: 系统性能和使用情况

## 技术架构

### 前端
- **React 18**: 现代化的用户界面
- **Ant Design**: 企业级 UI 组件库
- **Axios**: HTTP 客户端
- **Moment.js**: 时间处理

### 后端
- **FastAPI**: 高性能 Python Web 框架
- **Pydantic**: 数据验证和序列化
- **MoviePy**: 视频处理库
- **OpenAI API**: AI 脚本生成

### 依赖服务
- **FFmpeg**: 视频音频处理
- **TTS 引擎**: 文本转语音服务

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- FFmpeg
- OpenAI API Key

### 一键安装

```bash
# 自动安装所有依赖
python install.py
```

### 手动安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd ai-video-maker
   ```

2. **配置环境变量**
   ```bash
   cp backend/.env.example backend/.env
   # 编辑 .env 文件，填入你的 OpenAI API Key
   ```

3. **安装依赖**
   ```bash
   # 后端依赖
   cd backend
   pip install -r requirements.txt
   cd ..
   
   # 前端依赖
   cd frontend
   npm install
   cd ..
   ```

4. **启动服务**
   ```bash
   python start.py
   ```

5. **访问应用**
   - 前端: http://localhost:3000
   - 后端 API: http://localhost:8000
   - API 文档: http://localhost:8000/docs

### 故障排除

如果遇到问题，可以尝试:

```bash
# 检查系统状态
python check_status.py

# 修复前端依赖问题
python fix-frontend.py

# 运行功能测试
python test_features.py
```

详细的故障排除指南请查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### 云存储配置（可选）

平台支持自动将生成的视频上传到云存储：

```bash
# 在 backend/.env 中配置云存储（任选一种）
# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket

# 阿里云 OSS
ALIYUN_ACCESS_KEY=your_access_key
ALIYUN_SECRET_KEY=your_secret_key
ALIYUN_OSS_BUCKET=your_bucket
ALIYUN_OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
```

详细配置请查看 [CLOUD_STORAGE.md](CLOUD_STORAGE.md)

## 使用指南

### 🎯 功能入口

**方式一：完整制作流程**
1. 在首页输入视频主题
2. 点击"生成脚本"，AI 将自动生成视频脚本
3. 点击"配置视频"进入编辑界面
4. 在标签页中使用各种编辑功能

**方式二：直接管理资源**

### 2. 高级编辑

#### 文字样式
- 在"文字样式"标签页中自定义字体、颜色、位置
- 支持多种文字动画效果
- 实时预览文字效果

#### 时间轴编辑
- 在"时间轴"标签页中查看和编辑场景
- 调整场景时长和播放顺序
- 精确控制视频节奏

#### 素材管理
- 在"素材库"中上传图片、视频、音频文件
- 支持文件分类和搜索
- 拖拽添加素材到项目中

#### 音频管理
- 上传背景音乐和音效文件
- 设置音频音量和淡入淡出
- 为不同场景添加音效

#### 转场效果
- 选择场景间的转场动画
- 调整转场时长和缓动效果
- 预览转场效果

### 3. 导出视频

1. 在"导出设置"中配置视频参数
2. 选择分辨率、帧率、编码格式
3. 设置音频质量和编码
4. 点击"开始导出"生成视频

### 4. 项目管理

1. 在"项目管理"中保存当前项目
2. 为项目添加名称、描述、分类、标签
3. 浏览和加载历史项目
4. 复制或删除项目

## API 文档

启动服务后访问 http://localhost:8000/docs 查看完整的 API 文档。

### 主要 API 端点

- `POST /api/script/generate` - 生成视频脚本
- `POST /api/video/create` - 创建视频
- `GET /api/video/status/{video_id}` - 查询视频状态
- `POST /api/user-assets/upload` - 上传素材文件
- `POST /api/projects/save` - 保存项目
- `GET /api/projects/list` - 获取项目列表

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 必填 |
| `OPENAI_MODEL` | OpenAI 模型 | gpt-3.5-turbo |
| `MAX_VIDEO_DURATION` | 最大视频时长(秒) | 300 |
| `DEFAULT_VIDEO_RESOLUTION` | 默认视频分辨率 | 1280x720 |
| `DEFAULT_TTS_PROVIDER` | 默认 TTS 提供商 | gtts |

### 文件结构

```
ai-video-maker/
├── backend/                 # 后端代码
│   ├── routers/            # API 路由
│   ├── main.py             # 主应用文件
│   ├── requirements.txt    # Python 依赖
│   └── .env               # 环境变量
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/    # React 组件
│   │   └── App.js         # 主应用组件
│   ├── package.json       # Node.js 依赖
│   └── public/            # 静态文件
├── assets/                 # 静态资源
├── output/                 # 输出文件
├── uploads/               # 上传文件
├── data/                  # 数据存储
├── start.py               # 启动脚本
└── README.md              # 说明文档
```

## 开发指南

### 添加新功能

1. **后端 API**
   - 在 `backend/routers/` 中创建新的路由文件
   - 在 `main.py` 中注册路由
   - 使用 Pydantic 模型定义数据结构

2. **前端组件**
   - 在 `frontend/src/components/` 中创建新组件
   - 使用 Ant Design 组件库
   - 通过 Axios 调用后端 API

### 代码规范

- 后端使用 Python PEP 8 规范
- 前端使用 ESLint 和 Prettier
- 提交前运行测试确保代码质量

### 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t ai-video-maker .

# 运行容器
docker run -p 3000:3000 -p 8000:8000 ai-video-maker
```

### 生产环境

1. 设置环境变量 `ENVIRONMENT=production`
2. 配置反向代理 (Nginx)
3. 使用进程管理器 (PM2, Supervisor)
4. 配置 HTTPS 证书

## 常见问题

### Q: 视频生成失败怎么办？
A: 检查 FFmpeg 是否正确安装，查看后端日志获取详细错误信息。

### Q: 如何添加自定义模板？
A: 在 `templates/` 目录中添加模板文件，参考现有模板格式。

### Q: 支持哪些音频格式？
A: 支持 MP3, WAV, AAC, OGG, FLAC 等常见音频格式。

### Q: 如何提高视频生成速度？
A: 启用硬件加速，使用较低的视频质量设置，或升级服务器硬件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题请提交 Issue 或联系开发团队。