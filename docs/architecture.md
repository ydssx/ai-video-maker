# AI短视频制作平台 架构文档

> 版本: v1.0  |  日期: 2025-08-20  |  作者: Architect Agent

---

## 1. 引言

本文件描述 AI 短视频制作平台的整体系统架构，涵盖后端服务、数据层、外部依赖与非功能性特性，作为研发与运维协作的统一技术蓝图。系统目前已具备完善的前后端能力，本文聚焦后端与跨层面的系统设计。前端架构细节请结合 `docs/front-end-spec.md` 与仓库 `frontend/` 代码查看。

- 参考文档: `docs/PRD_20240818.md`, `docs/prd.md`, `README.md`, `BACKEND_ENHANCEMENT.md`, `COMPLETION_SUMMARY.md`, `PROGRESS_SUMMARY.md`
- 架构目标: 高可用、可维护、可扩展、性能优先，满足 PRD 中功能与 NFR 要求


## 2. 高层架构概览

### 2.1 技术摘要
- 架构风格: 分层架构 + 面向服务的组织（单体内模块化），异步任务通过消息队列解耦
- 主要组件: 前端 React、后端 FastAPI、服务层（AI/视频/文件/数据库/云存储）、消息队列、数据库与文件存储
- 关键技术: React 18、FastAPI、Pydantic、MoviePy、FFmpeg、OpenAI、SQLite/MySQL、Redis+Celery（按 PRD 规划）、Nginx
- 设计要点: 职责清晰、接口稳定、异步化长耗时任务、可观测性与错误处理完善

### 2.2 高层数据流/交互
- 用户操作 → 前端（React）→ 后端 API（FastAPI 路由）→ 服务层处理 → 数据库/文件存储 → 响应 → 前端状态更新
- 长耗时任务（如视频合成）→ 提交异步任务（Celery）→ Worker 执行 → 进度/结果持久化 → 前端轮询/WS 反馈

### 2.3 高层架构图

```mermaid
flowchart LR
    user[用户 / 浏览器] -->|HTTP/HTTPS| fe[前端 React 应用]
    fe -->|REST/WS| api[FastAPI 应用 (Routers + Middlewares)]

    subgraph Services[服务层]
        ai[AI 服务\n(OpenAI 脚本/关键词/情感)]
        vs[视频服务\n(MoviePy/FFmpeg 合成/转场)]
        fs[文件服务\n(上传/校验/缩略图/去重)]
        dbs[数据库服务\n(ORM/统计/配额/事务)]
        css[云存储服务\n(可选: OSS/S3)]
    end

    api --> ai
    api --> vs
    api --> fs
    api --> dbs
    api --> css

    subgraph MQ[消息队列 / 异步执行]
        redis[(Redis)]
        worker[Celery Workers]
    end

    api -->|异步任务| redis
    worker -->|取任务/回写结果| dbs
    worker --> vs
    worker --> fs

    subgraph Data[数据与文件]
        sql[(SQLite / MySQL)]
        store[(本地文件存储 / 云存储)]
    end

    dbs --> sql
    fs --> store
    css --> store

    subgraph External[外部服务]
        openai[OpenAI API]
        tts[TTS 引擎: Google/Edge/OpenAI]
        oss[云存储: 阿里云 OSS (可选)]
    end

    ai --> openai
    vs --> tts
    css --> oss
```


## 3. 架构与设计模式
- 分层架构（接口/路由层 → 服务层 → 数据/文件层）
- 模块化服务拆分：`ai_service`、`video_service`、`file_service`、`database_service`、`cloud_storage`
- 异步任务与解耦：Redis + Celery（依据 PRD 规划），将长耗时视频处理与主请求线程解耦
- 配置与环境隔离：`.env`、Docker Compose、多环境变量控制
- 健壮性策略：统一错误处理、中间件限流、重试与降级（参见 `middleware/` 与服务内实现）
- 可观测性：健康检查、性能与使用统计、结构化日志
- 安全性：JWT 鉴权、输入校验、文件类型/大小校验、最小权限访问


## 4. 组件视图与职责

### 4.1 API 与中间件
- 路由组：`/api/video/*`, `/api/script/*`, `/api/users/*`, `/api/system/*`, `/api/assets/*` 等（详见 `backend/routers/`）
- 中间件：错误处理、访问日志、限流（`backend/middleware/`）

### 4.2 服务层组件
- AI 服务（`services/ai_service.py`）
  - 职责：脚本生成、内容优化、关键词/情感分析、多 TTS 引擎
  - 关键接口：脚本生成、TTS 预览、缓存与重试
- 视频服务（`services/video_service.py`）
  - 职责：模板化合成、转场、音频集成、进度跟踪
  - 关键接口：生成/查询状态/下载/缩略图
- 文件服务（`services/file_service.py`）
  - 职责：上传、校验、缩略图、去重、存储清理
- 数据库服务（`services/database_service.py` / 可选 `mysql_database_service.py`）
  - 职责：用户/项目/视频/素材/统计/配额、事务与连接池
- 云存储服务（`services/cloud_storage.py`）
  - 职责：与 OSS/S3 等对接（可选）

### 4.3 数据与存储
- 数据库：开发默认 SQLite；生产可切换 MySQL（`setup_mysql*.py`）
- 文件存储：本地磁盘为主；可选云存储（阿里云 OSS 等）
- 表设计（节选，详见 `BACKEND_ENHANCEMENT.md`）
  - `users`, `projects`, `videos`, `assets`, `usage_stats`, `system_config`


## 5. 外部依赖与接口
- OpenAI API：脚本生成、内容优化等；需 `OPENAI_API_KEY`；注意速率/费用控制
- TTS 引擎：Google/Edge/OpenAI；需管理语速/语种与配额
- 云存储：阿里云 OSS（可选）；仅在配置启用时使用
- FFmpeg：视频/音频编解码运行时依赖

安全与合规：
- 秘钥管理：仅通过环境变量或安全配置注入
- 超时/重试：外部调用建议设置合理重试与超时
- 速率限制：对外部 API 调用设置配额与限流


## 6. 技术栈与运行时
- 前端：React 18、Ant Design、Axios
- 后端：FastAPI、Pydantic、Uvicorn/Gunicorn
- 处理：MoviePy、FFmpeg
- 数据库：SQLite（默认）/ MySQL（生产）
- 消息队列：Redis + Celery（按 PRD 规划）
- 部署：Docker / Docker Compose、Nginx 反向代理


## 7. 质量属性与目标（NFR 对齐）
- 性能：响应时间 < 2s（常规）；长耗时任务异步化；缓存与并发优化
- 可用性：目标 99.5%+；蓝绿发布、回滚策略
- 可靠性：统一错误处理、重试、降级与幂等性考量
- 可维护性：模块边界清晰、类型与文档完善、测试覆盖目标 ≥ 80%
- 可观测性：健康检查、性能/使用指标、结构化日志与追踪
- 安全性：JWT、输入与文件校验、最小权限、机密管理


## 8. 接口与契约（概览）
- 视频：`POST /api/video/generate`, `GET /api/video/status/{id}`, `GET /api/video/download/{id}`
- 脚本：`POST /api/script/generate`
- 资产：`POST /api/user-assets/upload`
- 项目：`POST /api/projects/save`, `GET /api/projects/list`
- 系统：`GET /api/system/health`, `GET /api/system/performance`

注意：接口以现有实现为准，新增异步化接口需返回任务 ID，并提供状态轮询/推送能力。


## 9. 部署与运行
- 开发：`python install.py` → `python start.py`
- 生产：Docker 化，`docker-compose.yml` + Nginx；开启 `ENVIRONMENT=production`
- MySQL：通过 `setup_mysql_simple.py` / `setup_mysql.py` 初始化；`migrate_to_mysql.py` 支持迁移
- 异步：新增 `celery` worker 与 `redis` 服务（参考 PRD 规划）

推荐部署拓扑：
- Web (Nginx) → FastAPI 应用 → Celery Workers → Redis → DB/存储


## 10. 监控与日志
- 健康检查：`/api/system/health`
- 性能指标：`/api/system/performance`
- 使用与业务统计：`usage_stats`、日志与分析脚本
- 日志：按服务与请求维度输出，建议启用轮转与集中采集


## 11. 风险与缓解
- 异步一致性：通过任务状态表与幂等设计降低重复与丢失风险
- 数据库瓶颈：使用连接池、索引与慢查询优化；必要时读写分离
- 外部依赖不稳定：超时、退避重试与降级；缓存热点结果
- 大文件与资源占用：分块上传、限流、资源回收与清理


## 12. 关键决策（摘要）
- 单体内模块化 + 异步任务：在复杂度与交付速度间平衡
- SQLite→MySQL 的可切换：开发便捷与生产稳定的兼容
- 可选云存储：按需启用，避免过早复杂化


## 13. 变更日志
- 2025-08-20 v1.0 初始化架构文档与高层图谱

---

如需细化到子系统级别（例如详细的组件/序列图、ER 图与容量规划），请提出具体关注点，我将补充相应章节与图表。
