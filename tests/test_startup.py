#!/usr/bin/env python3
"""
快速启动测试脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试关键模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试中间件导入
        from backend.middleware.logging import setup_logging
        print("✅ 日志中间件导入成功")
        
        from backend.middleware.rate_limiter import rate_limit_middleware
        print("✅ 限流中间件导入成功")
        
        from backend.middleware.error_handler import error_handling_middleware
        print("✅ 错误处理中间件导入成功")
        
        # 测试配置导入
        from backend.simple_config import settings
        print("✅ 配置模块导入成功")
        
        # 测试验证器导入
        from backend.utils.validators import security_validator
        print("✅ 验证器模块导入成功")
        
        # 测试模型导入
        from backend.models import VideoRequest
        print("✅ 数据模型导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {str(e)}")
        return False

def test_directories():
    """测试必要目录"""
    print("\n📁 测试目录结构...")
    
    directories = [
        "backend/logs",
        "backend/data",
        "backend/data/uploads",
        "backend/data/output", 
        "backend/data/temp",
        "backend/cache"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ 创建目录: {directory}")
        else:
            print(f"✅ 目录存在: {directory}")
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    print("\n⚙️ 测试基本功能...")
    
    try:
        # 测试配置
        from backend.simple_config import settings
        print(f"✅ 应用名称: {settings.app_name}")
        print(f"✅ 环境: {settings.environment}")
        print(f"✅ 调试模式: {settings.debug}")
        
        # 测试验证器
        from backend.utils.validators import security_validator
        
        # 测试模板ID验证
        valid_id = security_validator.validate_template_id("default")
        print(f"✅ 模板ID验证: {valid_id}")
        
        # 测试文件名验证
        valid_filename = security_validator.validate_filename("test.jpg")
        print(f"✅ 文件名验证: {valid_filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始启动测试")
    print("=" * 40)
    
    results = {}
    results["目录结构"] = test_directories()
    results["模块导入"] = test_imports()
    results["基本功能"] = test_basic_functionality()
    
    # 生成报告
    print("\n" + "=" * 40)
    print("📊 启动测试报告")
    print("=" * 40)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    success_rate = passed_tests / total_tests * 100
    
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"成功率: {success_rate:.1f}%")
    
    print("\n详细结果:")
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    if success_rate == 100:
        print("\n🎉 所有测试通过！可以启动后端服务。")
        print("💡 运行: python start.py")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")
    
    return success_rate == 100

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)