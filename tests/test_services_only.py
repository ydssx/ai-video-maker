#!/usr/bin/env python3
"""
服务模块独立测试脚本
不依赖HTTP服务，直接测试服务模块
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_service():
    """测试数据库服务"""
    print("🗄️ 测试数据库服务...")
    
    try:
        from backend.services.database_service import db_service
        
        # 测试数据库初始化
        print("✅ 数据库服务导入成功")
        
        # 测试系统统计
        stats = db_service.get_system_stats()
        print(f"✅ 系统统计获取成功: {stats}")
        
        # 测试配置功能
        db_service.set_config("test_key", "test_value")
        value = db_service.get_config("test_key")
        print(f"✅ 配置功能正常: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库服务测试失败: {str(e)}")
        return False

def test_file_service():
    """测试文件服务"""
    print("\n📁 测试文件服务...")
    
    try:
        from backend.services.file_service import file_service
        
        print("✅ 文件服务导入成功")
        
        # 测试存储统计
        stats = file_service.get_storage_stats()
        print(f"✅ 存储统计获取成功: {stats}")
        
        # 测试文件类型检测
        file_type = file_service.get_file_type("test.jpg")
        print(f"✅ 文件类型检测正常: {file_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ 文件服务测试失败: {str(e)}")
        return False

def test_ai_service():
    """测试AI服务"""
    print("\n🤖 测试AI服务...")
    
    try:
        from backend.services.ai_service import ai_service
        
        print("✅ AI服务导入成功")
        
        # 测试统计功能
        stats = ai_service.get_stats()
        print(f"✅ AI服务统计获取成功: {stats}")
        
        # 测试脚本生成（使用模板）
        script = asyncio.run(ai_service.generate_script("测试主题", "教育", "1分钟"))
        print(f"✅ 脚本生成成功: {script.get('title', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI服务测试失败: {str(e)}")
        return False

def test_video_service():
    """测试视频服务"""
    print("\n🎬 测试视频服务...")
    
    try:
        from backend.services.video_service import video_service
        
        print("✅ 视频服务导入成功")
        
        # 测试处理统计
        stats = video_service.get_processing_stats()
        print(f"✅ 视频处理统计获取成功: {stats}")
        
        # 测试模板样式
        template_style = video_service._get_template_style("default")
        print(f"✅ 模板样式获取成功: {template_style}")
        
        return True
        
    except Exception as e:
        print(f"❌ 视频服务测试失败: {str(e)}")
        return False

def test_models():
    """测试数据模型"""
    print("\n📋 测试数据模型...")
    
    try:
        from backend.models import ScriptRequest, VideoStyle, VideoDuration
        
        print("✅ 数据模型导入成功")
        
        # 测试模型创建
        request = ScriptRequest(
            topic="测试主题",
            style=VideoStyle.EDUCATIONAL,
            duration=VideoDuration.MEDIUM
        )
        print(f"✅ 模型创建成功: {request.topic}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据模型测试失败: {str(e)}")
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n📂 测试目录结构...")
    
    try:
        required_dirs = [
            "backend/services",
            "backend/routers", 
            "data",
            "data/uploads",
            "data/output",
            "data/temp"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)
                # 创建缺失的目录
                os.makedirs(dir_path, exist_ok=True)
                print(f"✅ 创建目录: {dir_path}")
            else:
                print(f"✅ 目录存在: {dir_path}")
        
        if missing_dirs:
            print(f"⚠️ 已创建缺失的目录: {missing_dirs}")
        
        return True
        
    except Exception as e:
        print(f"❌ 目录结构测试失败: {str(e)}")
        return False

def test_dependencies():
    """测试依赖项"""
    print("\n📦 测试依赖项...")
    
    dependencies = [
        ("fastapi", "FastAPI"),
        ("sqlite3", "SQLite3"),
        ("PIL", "Pillow"),
        ("moviepy", "MoviePy"),
        ("pydub", "PyDub"),
        ("requests", "Requests"),
        ("psutil", "PSUtil")
    ]
    
    results = []
    
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
            results.append(True)
        except ImportError:
            print(f"❌ {display_name} - 未安装")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 依赖项完整性: {success_rate:.1f}%")
    
    return success_rate > 80

def main():
    """主测试函数"""
    print("🚀 开始服务模块独立测试")
    print("=" * 50)
    
    # 运行所有测试
    results = {}
    
    results["目录结构"] = test_directory_structure()
    results["依赖项"] = test_dependencies()
    results["数据模型"] = test_models()
    results["数据库服务"] = test_database_service()
    results["文件服务"] = test_file_service()
    results["AI服务"] = test_ai_service()
    results["视频服务"] = test_video_service()
    
    # 生成测试报告
    print("\n" + "=" * 50)
    print("📊 服务模块测试报告")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    success_rate = passed_tests / total_tests * 100
    
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"成功率: {success_rate:.1f}%")
    
    print("\n详细结果:")
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print("\n🎯 服务状态评估:")
    if success_rate >= 90:
        print("🎉 服务模块优秀！可以启动HTTP服务进行完整测试。")
    elif success_rate >= 75:
        print("👍 服务模块良好，建议修复失败项后启动服务。")
    else:
        print("⚠️ 服务模块存在问题，需要先修复基础服务。")
    
    print("\n📋 下一步建议:")
    if success_rate >= 75:
        print("1. 运行 'python start.py' 启动完整服务")
        print("2. 运行 'python tests/test_backend_enhanced.py' 进行HTTP API测试")
    else:
        print("1. 安装缺失的依赖项: pip install -r requirements.txt")
        print("2. 检查并修复失败的服务模块")
        print("3. 确保所有必要的目录和文件存在")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)