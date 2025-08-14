#!/usr/bin/env python3
"""
数据库迁移脚本：从SQLite迁移到MySQL
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_service import DatabaseService
from services.mysql_database_service import MySQLDatabaseService
from database_factory import DatabaseFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """数据库迁移工具"""
    
    def __init__(self, sqlite_path: str, mysql_url: str):
        """
        初始化迁移工具
        
        Args:
            sqlite_path: SQLite数据库文件路径
            mysql_url: MySQL连接URL
        """
        self.sqlite_db = DatabaseService(sqlite_path)
        self.mysql_db = MySQLDatabaseService(mysql_url)
        
    def migrate_all_data(self) -> bool:
        """迁移所有数据"""
        try:
            logger.info("开始数据迁移...")
            
            # 1. 迁移用户数据
            self._migrate_users()
            
            # 2. 迁移项目数据
            self._migrate_projects()
            
            # 3. 迁移视频数据
            self._migrate_videos()
            
            # 4. 迁移素材数据
            self._migrate_assets()
            
            # 5. 迁移使用统计
            self._migrate_usage_stats()
            
            # 6. 迁移系统配置
            self._migrate_system_config()
            
            logger.info("数据迁移完成！")
            return True
            
        except Exception as e:
            logger.error(f"数据迁移失败: {str(e)}")
            return False
    
    def _migrate_users(self):
        """迁移用户数据"""
        logger.info("迁移用户数据...")
        
        with self.sqlite_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            for user in users:
                user_dict = dict(user)
                
                # 创建用户
                user_id = self.mysql_db.create_user(
                    username=user_dict['username'],
                    email=user_dict['email']
                )
                
                # 更新其他字段
                update_data = {}
                if user_dict['last_login']:
                    update_data['last_login'] = user_dict['last_login']
                if user_dict['settings']:
                    update_data['settings'] = json.loads(user_dict['settings'])
                if user_dict['quota_data']:
                    update_data['quota_data'] = json.loads(user_dict['quota_data'])
                
                if update_data:
                    self.mysql_db.update_user(user_id, **update_data)
                
                logger.info(f"迁移用户: {user_dict['username']} (ID: {user_dict['id']} -> {user_id})")
    
    def _migrate_projects(self):
        """迁移项目数据"""
        logger.info("迁移项目数据...")
        
        with self.sqlite_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects")
            projects = cursor.fetchall()
            
            for project in projects:
                project_dict = dict(project)
                
                script_data = None
                if project_dict['script_data']:
                    script_data = json.loads(project_dict['script_data'])
                
                success = self.mysql_db.create_project(
                    project_id=project_dict['id'],
                    user_id=project_dict['user_id'],
                    name=project_dict['name'],
                    description=project_dict['description'],
                    script_data=script_data
                )
                
                if success:
                    # 更新其他字段
                    update_data = {}
                    if project_dict['config_data']:
                        update_data['config_data'] = json.loads(project_dict['config_data'])
                    if project_dict['status']:
                        update_data['status'] = project_dict['status']
                    
                    if update_data:
                        self.mysql_db.update_project(project_dict['id'], **update_data)
                    
                    logger.info(f"迁移项目: {project_dict['name']} (ID: {project_dict['id']})")
    
    def _migrate_videos(self):
        """迁移视频数据"""
        logger.info("迁移视频数据...")
        
        with self.sqlite_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos")
            videos = cursor.fetchall()
            
            for video in videos:
                video_dict = dict(video)
                
                success = self.mysql_db.create_video(
                    video_id=video_dict['id'],
                    project_id=video_dict['project_id'],
                    user_id=video_dict['user_id'],
                    title=video_dict['title'],
                    duration=video_dict['duration'] or 0
                )
                
                if success:
                    # 更新其他字段
                    update_data = {}
                    if video_dict['file_path']:
                        update_data['file_path'] = video_dict['file_path']
                    if video_dict['thumbnail_path']:
                        update_data['thumbnail_path'] = video_dict['thumbnail_path']
                    if video_dict['status']:
                        update_data['status'] = video_dict['status']
                    
                    if update_data:
                        self.mysql_db.update_video(video_dict['id'], **update_data)
                    
                    logger.info(f"迁移视频: {video_dict['title']} (ID: {video_dict['id']})")
    
    def _migrate_assets(self):
        """迁移素材数据"""
        logger.info("迁移素材数据...")
        
        with self.sqlite_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM assets")
            assets = cursor.fetchall()
            
            for asset in assets:
                asset_dict = dict(asset)
                
                metadata = {}
                if asset_dict['metadata']:
                    metadata = json.loads(asset_dict['metadata'])
                
                success = self.mysql_db.create_asset(
                    asset_id=asset_dict['id'],
                    user_id=asset_dict['user_id'],
                    filename=asset_dict['filename'],
                    file_path=asset_dict['file_path'],
                    file_type=asset_dict['file_type'],
                    file_size=asset_dict['file_size'] or 0,
                    metadata=metadata
                )
                
                if success:
                    logger.info(f"迁移素材: {asset_dict['filename']} (ID: {asset_dict['id']})")
    
    def _migrate_usage_stats(self):
        """迁移使用统计"""
        logger.info("迁移使用统计...")
        
        with self.sqlite_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usage_stats")
            stats = cursor.fetchall()
            
            for stat in stats:
                stat_dict = dict(stat)
                
                action_data = None
                if stat_dict['action_data']:
                    action_data = json.loads(stat_dict['action_data'])
                
                self.mysql_db.log_usage(
                    user_id=stat_dict['user_id'],
                    action_type=stat_dict['action_type'],
                    action_data=action_data
                )
            
            logger.info(f"迁移了 {len(stats)} 条使用统计")
    
    def _migrate_system_config(self):
        """迁移系统配置"""
        logger.info("迁移系统配置...")
        
        with self.sqlite_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM system_config")
            configs = cursor.fetchall()
            
            for config in configs:
                config_dict = dict(config)
                
                try:
                    value = json.loads(config_dict['value'])
                except json.JSONDecodeError:
                    value = config_dict['value']
                
                self.mysql_db.set_config(config_dict['key'], value)
                logger.info(f"迁移配置: {config_dict['key']}")
    
    def verify_migration(self) -> bool:
        """验证迁移结果"""
        logger.info("验证迁移结果...")
        
        try:
            # 比较记录数量
            sqlite_stats = self.sqlite_db.get_system_stats()
            mysql_stats = self.mysql_db.get_system_stats()
            
            logger.info("SQLite统计:")
            for key, value in sqlite_stats.items():
                logger.info(f"  {key}: {value}")
            
            logger.info("MySQL统计:")
            for key, value in mysql_stats.items():
                logger.info(f"  {key}: {value}")
            
            # 检查关键数据是否一致
            if (sqlite_stats.get('total_users') == mysql_stats.get('total_users') and
                sqlite_stats.get('total_projects') == mysql_stats.get('total_projects') and
                sqlite_stats.get('total_videos') == mysql_stats.get('total_videos')):
                logger.info("[SUCCESS] 迁移验证通过")
                return True
            else:
                logger.warning("[WARNING] 迁移验证发现数据不一致")
                return False
                
        except Exception as e:
            logger.error(f"迁移验证失败: {str(e)}")
            return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库迁移工具")
    parser.add_argument("--sqlite-path", default="data/app.db", help="SQLite数据库文件路径")
    parser.add_argument("--mysql-url", required=True, help="MySQL连接URL")
    parser.add_argument("--verify-only", action="store_true", help="仅验证迁移结果")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.sqlite_path):
        logger.error(f"SQLite数据库文件不存在: {args.sqlite_path}")
        return 1
    
    if not DatabaseFactory.validate_mysql_url(args.mysql_url):
        logger.error("MySQL连接URL格式无效")
        logger.info("正确格式: mysql+pymysql://username:password@host:port/database")
        return 1
    
    try:
        migrator = DatabaseMigrator(args.sqlite_path, args.mysql_url)
        
        if args.verify_only:
            success = migrator.verify_migration()
        else:
            success = migrator.migrate_all_data()
            if success:
                migrator.verify_migration()
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"迁移过程出错: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())