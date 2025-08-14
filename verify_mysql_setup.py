#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证MySQL设置是否正确
"""

import sys
import os

def test_imports():
    """测试导入"""
    try:
        print("测试导入...")
        
        # 测试基本导入
        sys.path.append('backend')
        from services.mysql_database_service import MySQLDatabaseService
        from database_factory import DatabaseFactory
        
        print("[OK] 所有模块导入成功")
        return True
        
    except Exception as e:
        print(f"[ERROR] 导入失败: {str(e)}")
        return False

def test_model_definitions():
    """测试模型定义"""
    try:
        print("测试模型定义...")
        
        sys.path.append('backend')
        from services.mysql_database_service import Base
        
        # 检查表定义
        tables = Base.metadata.tables
        expected_tables = ['users', 'projects', 'videos', 'assets', 'usage_stats', 'system_config']
        
        for table_name in expected_tables:
            if table_name not in tables:
                print(f"[ERROR] 缺少表定义: {table_name}")
                return False
        
        print(f"[OK] 所有表定义正确: {list(tables.keys())}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 模型定义测试失败: {str(e)}")
        return False

def test_url_validation():
    """测试URL验证"""
    try:
        print("测试URL验证...")
        
        sys.path.append('backend')
        from database_factory import DatabaseFactory
        
        # 测试有效URL
        valid_urls = [
            "mysql+pymysql://user:pass@localhost:3306/db",
            "mysql+pymysql://root:password@127.0.0.1:3306/ai_video_maker"
        ]
        
        # 测试无效URL
        invalid_urls = [
            "invalid_url",
            "mysql://user:pass@host/db",  # 缺少pymysql
            "sqlite:///test.db"
        ]
        
        for url in valid_urls:
            if not DatabaseFactory.validate_mysql_url(url):
                print(f"[ERROR] 有效URL被误判为无效: {url}")
                return False
        
        for url in invalid_urls:
            if DatabaseFactory.validate_mysql_url(url):
                print(f"[ERROR] 无效URL被误判为有效: {url}")
                return False
        
        print("[OK] URL验证功能正常")
        return True
        
    except Exception as e:
        print(f"[ERROR] URL验证测试失败: {str(e)}")
        return False

def test_database_factory():
    """测试数据库工厂"""
    try:
        print("测试数据库工厂...")
        
        sys.path.append('backend')
        from database_factory import DatabaseFactory
        
        # 测试SQLite创建
        sqlite_service = DatabaseFactory.create_database_service("sqlite:///test_temp.db")
        if not sqlite_service:
            print("[ERROR] SQLite服务创建失败")
            return False
        
        # 清理测试文件
        if os.path.exists("test_temp.db"):
            os.remove("test_temp.db")
        
        print("[OK] 数据库工厂功能正常")
        return True
        
    except Exception as e:
        print(f"[ERROR] 数据库工厂测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=== MySQL设置验证 ===")
    print()
    
    tests = [
        ("导入测试", test_imports),
        ("模型定义测试", test_model_definitions),
        ("URL验证测试", test_url_validation),
        ("数据库工厂测试", test_database_factory)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"运行 {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("[SUCCESS] 所有测试通过，MySQL设置正确！")
        return 0
    else:
        print("[ERROR] 部分测试失败，请检查设置")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print("用户取消测试")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 测试过程出错: {str(e)}")
        sys.exit(1)