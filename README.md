# 短镜 · AI 短视频制作平台（v2 重写）

从零重写的 AI 短视频工具：主题 → 脚本 → MoviePy 渲染 → 下载。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 · TypeScript · Ant Design 5 |
| 后端 | FastAPI · SQLAlchemy 2 · Pydantic v2 |
| 数据库 | MySQL 8 |
| 渲染 | MoviePy |

## 快速开始

### 1. MySQL
```bash
# 默认账号 root / 123456，库 ai_video_maker
mysql -uroot -p123456 -e "CREATE DATABASE IF NOT EXISTS ai_video_maker CHARACTER SET utf8mb4;"
```

### 2. 后端
```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 前端
```bash
cd frontend
npm install
BROWSER=none npm start
```

打开 http://localhost:3000 ，注册账号后即可生成脚本并渲染。

可选：在 `.env` 中配置 `OPENAI_API_KEY` 以启用模型写脚本（否则走本地模板）。

## 目录

```
backend/app/          # 新后端包（api / core / db / models / schemas / services）
frontend/src/         # 新前端（auth + studio）
tests/                # pytest
```

## 许可证

与仓库原项目一致。
