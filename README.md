# AI 短视频制作平台

## 功能特性
- 文本转视频脚本生成
- 多种视频模板（默认、现代、科技、优雅）
- 语音合成（Google TTS / OpenAI TTS）
- 基础素材库管理
- MP4 视频导出

## 技术栈
- 后端：Python FastAPI
- 前端：React + Ant Design
- 视频处理：MoviePy
- 语音合成：Google TTS / OpenAI TTS
- AI 服务：OpenAI API

## 项目结构
```
ai-video-maker/
├── backend/          # Python 后端
├── frontend/         # React 前端
├── templates/        # 视频模板
├── assets/          # 素材库
└── output/          # 生成的视频
```

## 快速开始

### 开发环境
1. **安装依赖**
   ```bash
   cd ai-video-maker
   python install.py
   ```

2. **配置环境变量**
   - 编辑 `backend/.env` 文件
   - 添加 OpenAI API 密钥

3. **启动服务**
   ```bash
   python start.py
   ```

4. **访问应用**
   - 前端：http://localhost:3000
   - API 文档：http://localhost:8000/docs

### 生产部署

#### 使用 Docker（推荐）
1. **环境准备**
   ```bash
   python deploy.py setup
   ```

2. **构建镜像**
   ```bash
   python deploy.py build
   ```

3. **启动服务**
   ```bash
   python deploy.py start
   ```

4. **管理服务**
   ```bash
   python deploy.py status  # 查看状态
   python deploy.py logs    # 查看日志
   python deploy.py stop    # 停止服务
   ```

#### 手动部署
1. 安装 Python 3.11+ 和 Node.js 18+
2. 安装 FFmpeg 和字体包
3. 配置 Nginx 反向代理
4. 使用 PM2 或 systemd 管理进程

## 故障排除

### 常见问题

#### 前端编译错误
```bash
# 检查导入问题
node check-imports.js

# 测试构建
python test-build.py
```

#### 视频下载问题
```bash
# 运行下载调试工具
python debug-download.py
```

#### 后端启动失败
1. 检查 Python 依赖：`pip install -r backend/requirements.txt`
2. 检查 FFmpeg 安装：`ffmpeg -version`
3. 检查环境变量：确保 `.env` 文件配置正确

#### 视频制作失败
1. 检查 output 目录权限
2. 确保有足够的磁盘空间
3. 检查网络连接（图片下载需要）

### 开发调试
```bash
# 检查所有模块导入
python test-imports.py

# 测试完整构建流程
python test-build.py

# 启动开发环境
python start.py
```