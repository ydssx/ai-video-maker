# AGENTS.md

## Cursor Cloud specific instructions

### Product Overview
AI 短视频制作平台 — a React 18 frontend + FastAPI backend web application for AI-powered short video creation.

### Architecture
- **Backend**: FastAPI (Python 3.12) on port 8000, entry point `backend/main.py`
- **Frontend**: React 18 (CRA) on port 3000, proxied to backend via `package.json` proxy setting
- **Database**: MySQL 8.0 (required — the `database_factory.py` always passes MySQL URL; SQLite fallback path is broken due to missing `DatabaseService` class)

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

### Key Gotchas

1. **`.env` file**: Copy from `backend/.env.example`. Several env vars in `.env.example` are NOT defined in the `Settings` model (`MAX_UPLOAD_SIZE`, `UPLOAD_DIR`, `DEFAULT_TTS_PROVIDER`, `DEFAULT_VOICE`, `CACHE_DIR`, `CACHE_EXPIRE_HOURS`). These must be commented out or pydantic-settings will raise "extra inputs not permitted".
2. **`CORS_ORIGINS`**: Must be JSON array format, e.g. `CORS_ORIGINS=["http://localhost:3000"]`, not a bare URL string.
3. **`bcrypt` version**: passlib requires bcrypt 4.x; bcrypt 5.x causes `ValueError: password cannot be longer than 72 bytes`. Pin to `bcrypt==4.0.1`.
4. **Missing pip dependencies**: `requirements.txt` is incomplete. Extra packages needed: `pydantic-settings`, `python-jose[cryptography]`, `passlib`, `bcrypt==4.0.1`, `email-validator`, `loguru`, `psutil`. Also `numpy==1.24.3` is incompatible with Python 3.12; use `numpy>=1.24,<2.0`.
5. **MySQL table schema mismatch**: The `mysql_database_service.py` creates a `users` table with different columns than the ORM model in `src/db/models/user.py`. You may need to add `updated_at` and `preferences` columns to the MySQL `users` table for the ORM-based user repository to work.

### Lint
Frontend uses CRA's ESLint: `cd frontend && npx eslint src/`

### Tests
Backend: `cd backend && python3 -m pytest ../tests/ --ignore=../tests/test_ai_service.py -v`
(`test_ai_service.py` has a broken import path `backend.services.ai_service`)
Frontend: `cd frontend && CI=true npx react-scripts test --watchAll=false --passWithNoTests`

### API Docs
Swagger UI available at http://localhost:8000/docs when backend is running.
