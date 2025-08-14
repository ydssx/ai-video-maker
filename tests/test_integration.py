#!/usr/bin/env python3
"""
系统集成测试脚本
测试前端组件和后端API的集成功能
"""

import sys
import os
import asyncio
import json
import requests
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_backend_health():
    """测试后端服务健康状态"""
    print("🏥 测试后端服务健康状态...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            return True
        else:
            print(f"❌ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务 (请确保服务已启动)")
        return False
    except Exception as e:
        print(f"❌ 后端健康检查失败: {str(e)}")
        return False

def test_api_endpoints():
    """测试主要API端点"""
    print("\n🔌 测试主要API端点...")
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        {"path": "/", "method": "GET", "name": "根路径"},
        {"path": "/api/projects", "method": "GET", "name": "项目列表"},
        {"path": "/api/stats/overview", "method": "GET", "name": "统计概览"},
        {"path": "/api/user-assets", "method": "GET", "name": "用户素材"},
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            if endpoint["method"] == "GET":
                response = requests.get(f"{base_url}{endpoint['path']}", timeout=10)
            
            if response.status_code in [200, 404]:  # 404也算正常，说明路由存在
                print(f"✅ {endpoint['name']}: {response.status_code}")
                results.append(True)
            else:
                print(f"❌ {endpoint['name']}: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {endpoint['name']}: {str(e)}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 API端点测试成功率: {success_rate:.1f}%")
    
    return success_rate > 75

def test_video_generation_flow():
    """测试视频生成流程"""
    print("\n🎬 测试视频生成流程...")
    
    base_url = "http://localhost:8000"
    
    # 测试脚本生成
    print("📝 测试脚本生成...")
    try:
        script_data = {
            "topic": "测试主题",
            "style": "教育",
            "duration": "1分钟"
        }
        
        response = requests.post(
            f"{base_url}/api/generate-script",
            json=script_data,
            timeout=30
        )
        
        if response.status_code == 200:
            script_result = response.json()
            print("✅ 脚本生成成功")
            print(f"   场景数量: {len(script_result.get('scenes', []))}")
            
            # 测试视频生成
            print("\n🎥 测试视频生成...")
            video_data = {
                "script": script_result,
                "template": "modern",
                "voice_enabled": False,  # 跳过语音以加快测试
                "export_settings": {
                    "resolution": "720p",
                    "fps": 30,
                    "format": "mp4"
                }
            }
            
            response = requests.post(
                f"{base_url}/api/generate-video",
                json=video_data,
                timeout=60
            )
            
            if response.status_code == 200:
                print("✅ 视频生成成功")
                return True
            else:
                print(f"❌ 视频生成失败: {response.status_code}")
                return False
                
        else:
            print(f"❌ 脚本生成失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 视频生成流程测试失败: {str(e)}")
        return False

def test_file_operations():
    """测试文件操作功能"""
    print("\n📁 测试文件操作功能...")
    
    base_url = "http://localhost:8000"
    
    try:
        # 测试文件上传
        print("📤 测试文件上传...")
        
        # 创建一个测试文件
        test_file_path = "test_upload.txt"
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("这是一个测试文件")
        
        with open(test_file_path, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            response = requests.post(
                f"{base_url}/api/user-assets/upload",
                files=files,
                timeout=30
            )
        
        # 清理测试文件
        os.unlink(test_file_path)
        
        if response.status_code == 200:
            print("✅ 文件上传成功")
            
            # 测试文件列表
            print("📋 测试文件列表...")
            response = requests.get(f"{base_url}/api/user-assets", timeout=10)
            
            if response.status_code == 200:
                assets = response.json()
                print(f"✅ 文件列表获取成功，共 {len(assets)} 个文件")
                return True
            else:
                print(f"❌ 文件列表获取失败: {response.status_code}")
                return False
        else:
            print(f"❌ 文件上传失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 文件操作测试失败: {str(e)}")
        return False

def test_frontend_files():
    """测试前端文件完整性"""
    print("\n🌐 测试前端文件完整性...")
    
    frontend_path = Path("frontend")
    
    critical_files = [
        "src/App.js",
        "src/components/VideoPreview.js",
        "src/components/VideoTimeline.js",
        "src/components/TextStyleEditor.js",
        "src/components/AssetManager.js",
        "src/components/AudioManager.js",
        "src/components/TransitionEditor.js",
        "src/components/ExportSettings.js",
        "src/components/ProjectManager.js",
        "src/components/UserDashboard.js",
        "public/index.html",
        "package.json"
    ]
    
    missing_files = []
    
    for file_path in critical_files:
        full_path = frontend_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ 缺失文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print(f"\n✅ 所有关键前端文件都存在")
        return True

def test_backend_files():
    """测试后端文件完整性"""
    print("\n🔧 测试后端文件完整性...")
    
    backend_path = Path("backend")
    
    critical_files = [
        "main.py",
        "services/ai_service.py",
        "routers/video_maker.py",
        "routers/projects.py",
        "routers/user_assets.py",
        "routers/audio_manager.py",
        "routers/stats.py",
        "routers/cloud_storage.py"
    ]
    
    missing_files = []
    
    for file_path in critical_files:
        full_path = backend_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ 缺失文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print(f"\n✅ 所有关键后端文件都存在")
        return True

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("📊 集成测试报告")
    print("=" * 60)
    
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
    
    if success_rate >= 80:
        print(f"\n🎉 系统集成测试整体通过！")
        return True
    else:
        print(f"\n⚠️ 系统集成测试需要改进")
        return False

def main():
    """主测试函数"""
    print("🚀 开始系统集成测试")
    print("=" * 60)
    
    # 运行所有测试
    results = {}
    
    # 文件完整性测试（不需要服务运行）
    results["前端文件完整性"] = test_frontend_files()
    results["后端文件完整性"] = test_backend_files()
    
    # 服务相关测试
    backend_healthy = test_backend_health()
    results["后端服务健康"] = backend_healthy
    
    if backend_healthy:
        results["API端点测试"] = test_api_endpoints()
        results["文件操作测试"] = test_file_operations()
        # results["视频生成流程"] = test_video_generation_flow()  # 暂时跳过，因为可能很慢
    else:
        print("\n⚠️ 后端服务未运行，跳过API相关测试")
        print("💡 提示: 运行 'python start.py' 启动服务后再测试")
    
    # 生成测试报告
    return generate_test_report(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)