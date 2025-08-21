import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, db_path: str = "data/app.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    settings TEXT DEFAULT '{}',
                    quota_data TEXT DEFAULT '{}'
                )
            ''')
            
            # 项目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    script_data TEXT,
                    config_data TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # 视频表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    user_id INTEGER,
                    title TEXT,
                    duration REAL,
                    file_path TEXT,
                    thumbnail_path TEXT,
                    status TEXT DEFAULT 'processing',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # 素材表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_type TEXT,
                    file_size INTEGER,
                    thumbnail_path TEXT,
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # 统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action_type TEXT,
                    action_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # 系统配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("数据库初始化完成")
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    # 用户管理
    def create_user(self, username: str, email: str = None) -> int:
        """创建用户"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email) VALUES (?, ?)",
                (username, email)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """获取用户信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                user = dict(row)
                if user['settings']:
                    user['settings'] = json.loads(user['settings'])
                if user['quota_data']:
                    user['quota_data'] = json.loads(user['quota_data'])
                return user
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """根据用户名获取用户信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                user = dict(row)
                if user['settings']:
                    user['settings'] = json.loads(user['settings'])
                if user['quota_data']:
                    user['quota_data'] = json.loads(user['quota_data'])
                return user
            return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """更新用户信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['settings', 'quota_data'] and isinstance(value, dict):
                    value = json.dumps(value)
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
    
    def update_user_login_time(self, user_id: int):
        """更新用户最后登录时间"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            conn.commit()
    
    def get_user_settings(self, user_id: int) -> Dict:
        """获取用户设置"""
        user = self.get_user(user_id)
        if user and user.get('settings'):
            return user['settings']
        return {}
    
    def get_user_quota(self, user_id: int) -> Optional[Dict]:
        """获取用户配额"""
        user = self.get_user(user_id)
        if user and user.get('quota_data'):
            return user['quota_data']
        return None
    
    def update_user_quota(self, user_id: int, quota_data: Dict):
        """更新用户配额"""
        return self.update_user(user_id, quota_data=quota_data)
    
    def get_user_usage_history(self, user_id: int, days: int = 30) -> List[Dict]:
        """获取用户使用历史"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            since_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT action_type, action_data, timestamp
                FROM usage_stats 
                WHERE user_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (user_id, since_date))
            
            history = []
            for row in cursor.fetchall():
                record = dict(row)
                if record['action_data']:
                    record['action_data'] = json.loads(record['action_data'])
                history.append(record)
            
            return history
    
    def delete_user_data(self, user_id: int) -> bool:
        """删除用户相关数据"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # 删除用户的统计数据
                cursor.execute("DELETE FROM usage_stats WHERE user_id = ?", (user_id,))
                
                # 删除用户的素材
                cursor.execute("DELETE FROM assets WHERE user_id = ?", (user_id,))
                
                # 删除用户的视频
                cursor.execute("DELETE FROM videos WHERE user_id = ?", (user_id,))
                
                # 删除用户的项目
                cursor.execute("DELETE FROM projects WHERE user_id = ?", (user_id,))
                
                # 最后删除用户
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                
                conn.commit()
                return True
                
            except Exception as e:
                conn.rollback()
                logger.error(f"删除用户数据失败: {str(e)}")
                return False
    
    def update_user_settings(self, user_id: int, settings: Dict):
        """更新用户设置"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET settings = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (json.dumps(settings), user_id)
            )
            conn.commit()
    
    # 项目管理
    def create_project(self, project_id: str, user_id: int, name: str, 
                      description: str = None, script_data: Dict = None) -> bool:
        """创建项目"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO projects (id, user_id, name, description, script_data)
                    VALUES (?, ?, ?, ?, ?)
                ''', (project_id, user_id, name, description, 
                     json.dumps(script_data) if script_data else None))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """获取项目"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                project = dict(row)
                if project['script_data']:
                    project['script_data'] = json.loads(project['script_data'])
                if project['config_data']:
                    project['config_data'] = json.loads(project['config_data'])
                return project
            return None
    
    def update_project(self, project_id: str, **kwargs) -> bool:
        """更新项目"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 构建更新语句
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['script_data', 'config_data'] and isinstance(value, dict):
                    value = json.dumps(value)
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            if not set_clauses:
                return False
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(project_id)
            
            query = f"UPDATE projects SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
    
    def get_user_projects(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """获取用户项目列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM projects 
                WHERE user_id = ? 
                ORDER BY updated_at DESC 
                LIMIT ? OFFSET ?
            ''', (user_id, limit, offset))
            
            projects = []
            for row in cursor.fetchall():
                project = dict(row)
                if project['script_data']:
                    project['script_data'] = json.loads(project['script_data'])
                if project['config_data']:
                    project['config_data'] = json.loads(project['config_data'])
                projects.append(project)
            
            return projects
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # 视频管理
    def create_video(self, video_id: str, project_id: str, user_id: int, 
                    title: str, duration: float = 0) -> bool:
        """创建视频记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO videos (id, project_id, user_id, title, duration)
                    VALUES (?, ?, ?, ?, ?)
                ''', (video_id, project_id, user_id, title, duration))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def update_video(self, video_id: str, **kwargs) -> bool:
        """更新视频信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(video_id)
            query = f"UPDATE videos SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
    
    def get_video(self, video_id: str) -> Optional[Dict]:
        """获取视频信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    # 素材管理
    def create_asset(self, asset_id: str, user_id: int, filename: str, 
                    file_path: str, file_type: str, file_size: int,
                    metadata: Dict = None) -> bool:
        """创建素材记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO assets (id, user_id, filename, file_path, file_type, file_size, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (asset_id, user_id, filename, file_path, file_type, file_size,
                     json.dumps(metadata) if metadata else '{}'))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_user_assets(self, user_id: int, file_type: str = None, 
                       limit: int = 50, offset: int = 0) -> List[Dict]:
        """获取用户素材列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if file_type:
                cursor.execute('''
                    SELECT * FROM assets 
                    WHERE user_id = ? AND file_type = ?
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                ''', (user_id, file_type, limit, offset))
            else:
                cursor.execute('''
                    SELECT * FROM assets 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                ''', (user_id, limit, offset))
            
            assets = []
            for row in cursor.fetchall():
                asset = dict(row)
                if asset['metadata']:
                    asset['metadata'] = json.loads(asset['metadata'])
                assets.append(asset)
            
            return assets
    
    def delete_asset(self, asset_id: str) -> bool:
        """删除素材"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # 统计功能
    def log_usage(self, user_id: int, action_type: str, action_data: Dict = None):
        """记录使用统计"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usage_stats (user_id, action_type, action_data)
                VALUES (?, ?, ?)
            ''', (user_id, action_type, json.dumps(action_data) if action_data else None))
            conn.commit()
    
    def get_user_stats(self, user_id: int, days: int = 30) -> Dict:
        """获取用户统计信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取指定天数内的统计
            since_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT action_type, COUNT(*) as count
                FROM usage_stats 
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY action_type
            ''', (user_id, since_date))
            
            stats = {}
            for row in cursor.fetchall():
                stats[row['action_type']] = row['count']
            
            return stats
    
    def get_system_stats(self) -> Dict:
        """获取系统统计信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # 总用户数
            cursor.execute("SELECT COUNT(*) as count FROM users")
            stats['total_users'] = cursor.fetchone()['count']
            
            # 总项目数
            cursor.execute("SELECT COUNT(*) as count FROM projects")
            stats['total_projects'] = cursor.fetchone()['count']
            
            # 总视频数
            cursor.execute("SELECT COUNT(*) as count FROM videos")
            stats['total_videos'] = cursor.fetchone()['count']
            
            # 今日活跃用户
            today = datetime.now().date()
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) as count 
                FROM usage_stats 
                WHERE DATE(timestamp) = ?
            ''', (today,))
            stats['active_users_today'] = cursor.fetchone()['count']
            
            return stats
    
    # 系统配置
    def set_config(self, key: str, value: Any):
        """设置系统配置"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO system_config (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, json.dumps(value) if not isinstance(value, str) else value))
            conn.commit()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取系统配置"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_config WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row['value'])
                except json.JSONDecodeError:
                    return row['value']
            return default
    
    def cleanup_old_data(self, days: int = 90):
        """清理旧数据"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 清理旧的使用统计
            cursor.execute(
                "DELETE FROM usage_stats WHERE timestamp < ?",
                (cutoff_date,)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            logger.info(f"清理了 {deleted_count} 条旧统计数据")
            return deleted_count

# 全局数据库服务实例
db_service = DatabaseService()