# AGENTS.md

## Cursor Cloud specific instructions

### Product Overview
**短镜（AI Video Maker）v2** — 从零重写的 React 18 + FastAPI 短视频制作平台。

### Architecture
- **Backend**: FastAPI（Python 3.12），入口 `backend/main.py`，包路径 `app/`
- **Frontend**: React 18 + TypeScript（CRA），端口 3000，proxy → 8000
- **Database**: MySQL 8.0 only（SQLAlchemy 2.0 单一 ORM）

### Running Services

**MySQL**:
```
sudo mkdir -p /var/run/mysqld && sudo chown mysql:mysql /var/run/mysqld && sudo chmod 777 /var/run/mysqld
sudo mysqld --user=mysql --datadir=/var/lib/mysql &
```
默认：`root` / `123456`，库名 `ai_video_maker`。

**Backend**:
```
cd backend
cp -n .env.example .env
pip install -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend**:
```
cd frontend
npm install
BROWSER=none npm start
```

### MVP API
- `POST /api/auth/register` · `POST /api/auth/login` · `GET /api/auth/me`
- `POST /api/script/generate` · `GET /api/script/templates`
- `POST /api/video/create` · `GET /api/video/{id}` · `GET /api/video/{id}/download`
- `CRUD /api/projects/`

### Tests
```
cd backend && python3 -m pytest ../tests -v
cd frontend && CI=true npx react-scripts test --watchAll=false --passWithNoTests
```

### API Docs
http://localhost:8000/docs
