#!/usr/bin/env python3
"""
测试MySQL数据库连接和模型定义
"""

import os
import sys
import logging

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mysql_models():
    """测试MySQL模型定义"""
    try:
        from services.mysql_database_service import MySQLDatabaseService, Base
        logger.info("[OK] MySQL模型导入成功")
        
        # 检查所有表的定义
        tables = Base.metadata.tables
        logger.info(f"定义的表: {list(tables.keys())}")
        
        for table_name, table in tables.items():
            logger.info(f"表 {table_name} 的列:")
            for column in table.columns:
                logger.info(f"  - {column.name}: {column.type}")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] MySQL模型测试失败: {str(e)}")
        return False

def test_database_factory():
    """测试数据库工厂"""
    try:
        from database_factory import DatabaseFactory
        
        # 测试SQLite
        sqlite_service = DatabaseFactory.create_database_service("sqlite:///test.db")
        logger.info("[OK] SQLite数据库服务创建成功")
        
        # 测试MySQL URL验证
        valid_url = "mysql+pymysql://user:pass@localhost:3306/test"
        invalid_url = "invalid_url"
        
        assert DatabaseFactory.validate_mysql_url(valid_url) == True
        assert DatabaseFactory.validate_mysql_url(invalid_url) == False
        logger.info("[OK] MySQL URL验证测试通过")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] 数据库工厂测试失败: {str(e)}")
        return False

def test_mysql_connection_with_url(mysql_url):
    """测试MySQL连接"""
    try:
        from services.mysql_database_service import MySQLDatabaseService
        
        logger.info(f"测试MySQL连接: {mysql_url}")
        db_service = MySQLDatabaseService(mysql_url)
        
        if db_service.test_connection():
            logger.info("[OK] MySQL连接测试成功")
            
            # 测试基本操作
            stats = db_service.get_system_stats()
            logger.info(f"系统统计: {stats}")
            
            return True
        else:
            logger.error("[ERROR] MySQL连接测试失败")
            return False
            
    except Exception as e:
        logger.error(f"[ERROR] MySQL连接测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="测试MySQL数据库连接")
    parser.add_argument("--mysql-url", help="MySQL连接URL")
    parser.add_argument("--test-models-only", action="store_true", help="仅测试模型定义")
    
    args = parser.parse_args()
    
    print("=== MySQL数据库测试 ===\n")
    
    # 测试模型定义
    if not test_mysql_models():
        return 1
    
    # 测试数据库工厂
    if not test_database_factory():
        return 1
    
    if args.test_models_only:
        print("\n[SUCCESS] 模型定义测试完成")
        return 0
    
    # 测试MySQL连接（如果提供了URL）
    if args.mysql_url:
        if not test_mysql_connection_with_url(args.mysql_url):
            return 1
        print("\n[SUCCESS] 所有测试通过")
    else:
        print("\n[SUCCESS] 模型和工厂测试通过")
        print("提示: 使用 --mysql-url 参数测试实际的MySQL连接")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())