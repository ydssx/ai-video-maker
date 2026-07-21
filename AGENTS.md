# AI 短视频制作平台

## Cursor Cloud specific instructions

### Product Overview
AI 短视频制作平台 — a React 18 frontend + FastAPI backend web application for AI-powered short video creation.

### Architecture
- **Backend**: FastAPI (Python 3.12) on port 8000, entry point `backend/main.py`
- **Frontend**: React 18 (CRA + TypeScript) on port 3000, proxied to backend via `package.json` proxy setting
- **Database**: MySQL 8.0 only（SQLite 回退已移除）

### Running Services

**MySQL** must be running before the backend starts:
```
sudo mkdir -p /var/run/mysqld && sudo chown mysql:mysql /var/run/mysqld && sudo chmod 777 /var/run/mysqld
sudo mysqld --user=mysql --datadir=/var/lib/mysql &
```
Default credentials: `root` / `123456`, database: `ai_video_maker`.

**Backend**:
```
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend**:
```
cd frontend && BROWSER=none npm start
```

### Key Notes

1. **`.env` file**: Copy from `backend/.env.example`. Settings 使用 `extra = "ignore"`，未知环境变量不会导致启动失败；请优先使用 `.env.example` 中的字段名。
2. **`CORS_ORIGINS`**: 支持 JSON 数组或逗号分隔，例如 `CORS_ORIGINS=["http://localhost:3000"]`。
3. **`bcrypt`**: 需锁定 `bcrypt==4.0.1`（passlib 不兼容 bcrypt 5.x）。
4. **依赖**: 见 `backend/requirements.txt`（含 pydantic-settings、python-jose、passlib、loguru、psutil 等）。numpy 使用 `>=1.26,<2.0` 以兼容 Python 3.12。
5. **用户表**: `mysql_database_service` 启动时会自动为 `users` 表补齐 `updated_at` / `preferences` 等与 ORM 对齐的列。
6. **API 模型**: 脚本/视频请求模型位于 `src/schemas/api_models.py`；根目录 `models.py` 仅为兼容再导出。

### Lint
Frontend uses CRA's ESLint: `cd frontend && npx eslint src/`

### Tests
Backend: `cd backend && python3 -m pytest ../tests/ -v`
Frontend: `cd frontend && CI=true npx react-scripts test --watchAll=false --passWithNoTests`

### API Docs
Swagger UI available at http://localhost:8000/docs when backend is running.
