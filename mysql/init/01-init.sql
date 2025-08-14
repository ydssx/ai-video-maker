-- AI视频制作平台 MySQL初始化脚本

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS ai_video_maker 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE ai_video_maker;

-- 创建用户（如果不存在）
-- 注意：在Docker环境中，用户会通过环境变量自动创建

-- 设置时区
SET time_zone = '+00:00';

-- 创建一些初始配置（可选）
-- 这些表会由应用程序自动创建，这里只是示例

-- 插入一些系统配置
-- INSERT INTO system_config (key, value) VALUES 
-- ('app_version', '1.0.0'),
-- ('maintenance_mode', 'false'),
-- ('max_users', '1000');

-- 创建索引优化查询性能（应用启动后执行）
-- CREATE INDEX idx_projects_user_id ON projects(user_id);
-- CREATE INDEX idx_projects_updated_at ON projects(updated_at);
-- CREATE INDEX idx_videos_user_id ON videos(user_id);
-- CREATE INDEX idx_videos_project_id ON videos(project_id);
-- CREATE INDEX idx_assets_user_id ON assets(user_id);
-- CREATE INDEX idx_assets_file_type ON assets(file_type);
-- CREATE INDEX idx_usage_stats_user_id ON usage_stats(user_id);
-- CREATE INDEX idx_usage_stats_timestamp ON usage_stats(timestamp);

-- 显示创建完成信息
SELECT 'AI视频制作平台数据库初始化完成' as message;