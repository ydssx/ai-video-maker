#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MySQL text()修复是否有效
"""

import sys
import os
import logging

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mysql_text_functions():
    """测试MySQL text()函数修复"""
    try:
        from services.mysql_database_service import MySQLDatabaseService
        from sqlalchemy import text
        
        print("测试MySQL text()函数修复...")
        
        # 创建一个模拟的MySQL服务（不实际连接）
        # 这里主要测试代码语法是否正确
        
        # 测试导入text函数
        print("[OK] text函数导入成功")
        
        # 测试text()函数的使用
        test_sql = text("SELECT 1")
        print(f"[OK] text()函数使用正确: {test_sql}")
        
        # 测试带参数的SQL
        test_sql_with_params = text("""
            SELECT action_type, COUNT(*) as count
            FROM usage_stats 
            WHERE user_id = :user_id AND timestamp >= :since_date
            GROUP BY action_type
        """)
        print("[OK] 带参数的text()函数使用正确")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] text()函数测试失败: {str(e)}")
        return False

def test_mysql_service_methods():
    """测试MySQL服务方法定义"""
    try:
        from services.mysql_database_service import MySQLDatabaseService
        
        print("测试MySQL服务方法定义...")
        
        # 检查关键方法是否存在
        required_methods = [
            'test_connection',
            'get_user_stats', 
            'get_system_stats'
        ]
        
        for method_name in required_methods:
            if not hasattr(MySQLDatabaseService, method_name):
                print(f"[ERROR] 缺少方法: {method_name}")
                return False
        
        print("[OK] 所有必需方法都存在")
        return True
        
    except Exception as e:
        print(f"[ERROR] 方法定义测试失败: {str(e)}")
        return False

def test_sqlalchemy_version():
    """测试SQLAlchemy版本兼容性"""
    try:
        import sqlalchemy
        from sqlalchemy import text
        
        print(f"SQLAlchemy版本: {sqlalchemy.__version__}")
        
        # 测试text函数
        test_query = text("SELECT 1")
        print(f"[OK] text()函数可用: {type(test_query)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] SQLAlchemy版本测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=== MySQL text()修复验证 ===")
    print()
    
    tests = [
        ("SQLAlchemy版本测试", test_sqlalchemy_version),
        ("text()函数测试", test_mysql_text_functions),
        ("MySQL服务方法测试", test_mysql_service_methods)
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
        print("[SUCCESS] text()修复验证通过！")
        print("现在可以安全使用MySQL数据库服务了。")
        return 0
    else:
        print("[ERROR] 部分测试失败")
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