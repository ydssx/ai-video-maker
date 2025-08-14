# MySQL数据库支持

AI视频制作平台现在支持MySQL数据库，提供更好的性能和并发处理能力。

## 快速开始

### 1. 自动设置（推荐）

运行交互式设置脚本：

```bash
python setup_mysql.py
```

脚本会引导你完成：
- 安装Python依赖
- 测试MySQL连接
- 创建数据库
- 更新配置文件
- 验证设置

### 2. 手动设置

#### 安装依赖

```bash
pip install sqlalchemy==2.0.23 pymysql==1.1.0 alembic==1.13.1
```

#### 配置环境变量

在 `backend/.env` 文件中添加：

```bash
# 使用MySQL数据库
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/ai_video_maker

# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=ai_video_maker
MYSQL_CHARSET=utf8mb4
```

#### 创建数据库

```sql
CREATE DATABASE ai_video_maker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 数据迁移

### 从SQLite迁移到MySQL

如果你已经有SQLite数据，可以使用迁移工具：

```bash
# 迁移数据
python backend/migrate_to_mysql.py --mysql-url "mysql+pymysql://user:password@host:port/database"

# 验证迁移结果
python backend/migrate_to_mysql.py --mysql-url "mysql+pymysql://user:password@host:port/database" --verify-only
```

## Docker部署

### 使用MySQL的Docker Compose

```bash
# 使用包含MySQL的配置
docker-compose -f docker-compose.mysql.yml up -d
```

### 环境变量配置

创建 `.env` 文件：

```bash
# MySQL配置
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_USER=aiuser
MYSQL_PASSWORD=password
MYSQL_DATABASE=ai_video_maker

# 应用配置
OPENAI_API_KEY=your_openai_api_key
```

## 测试连接

### 测试模型定义

```bash
python test_mysql_connection.py --test-models-only
```

### 测试数据库连接

```bash
python test_mysql_connection.py --mysql-url "mysql+pymysql://user:password@host:port/database"
```

## 性能优化

### 推荐的MySQL配置

在MySQL配置文件中添加：

```ini
[mysqld]
# 字符集设置
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

# 性能优化
innodb_buffer_pool_size=1G
innodb_log_file_size=256M
max_connections=200
query_cache_size=64M
```

### 索引优化

应用启动后，MySQL会自动创建必要的索引。你也可以手动添加：

```sql
-- 用户相关索引
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_updated_at ON projects(updated_at);
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_project_id ON videos(project_id);
CREATE INDEX idx_assets_user_id ON assets(user_id);
CREATE INDEX idx_assets_file_type ON assets(file_type);
CREATE INDEX idx_usage_stats_user_id ON usage_stats(user_id);
CREATE INDEX idx_usage_stats_timestamp ON usage_stats(timestamp);
```

## 故障排除

### 常见问题

1. **连接被拒绝**
   - 检查MySQL服务是否运行
   - 验证主机名和端口
   - 确认防火墙设置

2. **认证失败**
   - 检查用户名和密码
   - 确认用户有数据库访问权限
   - 对于MySQL 8.0，可能需要使用 `mysql_native_password`

3. **字符集问题**
   - 确保数据库使用 `utf8mb4` 字符集
   - 检查连接URL中的charset参数

### 调试命令

```bash
# 检查MySQL服务状态
systemctl status mysql  # Linux
brew services list | grep mysql  # macOS

# 测试MySQL连接
mysql -h localhost -u username -p

# 查看数据库字符集
SHOW VARIABLES LIKE 'character_set%';
```

## 数据库架构

### 主要表结构

- **users**: 用户信息
- **projects**: 项目数据
- **videos**: 视频记录
- **assets**: 素材文件
- **usage_stats**: 使用统计
- **system_config**: 系统配置

### 关系设计

- 用户 → 项目 (一对多)
- 用户 → 视频 (一对多)
- 用户 → 素材 (一对多)
- 项目 → 视频 (一对多)

## 备份和恢复

### 备份数据库

```bash
mysqldump -u username -p ai_video_maker > backup.sql
```

### 恢复数据库

```bash
mysql -u username -p ai_video_maker < backup.sql
```

## 监控和维护

### 查看数据库状态

```sql
-- 查看表大小
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'ai_video_maker';

-- 查看连接数
SHOW STATUS LIKE 'Threads_connected';

-- 查看慢查询
SHOW STATUS LIKE 'Slow_queries';
```

### 定期维护

```sql
-- 优化表
OPTIMIZE TABLE users, projects, videos, assets, usage_stats;

-- 分析表
ANALYZE TABLE users, projects, videos, assets, usage_stats;
```