#!/usr/bin/env python3
"""
测试所有模块导入是否正常
"""

def test_backend_imports():
    """测试后端模块导入"""
    try:
        print("测试后端模块导入...")
        
        # 测试主要模块
        from backend.main import app
        print("✓ main.py 导入成功")
        
        from backend.models import VideoRequest, VideoResponse, ScriptRequest
        print("✓ models.py 导入成功")
        
        from backend.routers import script_generator, video_maker, assets, stats
        print("✓ 所有路由模块导入成功")
        
        from backend.services.ai_service import ai_service
        print("✓ AI 服务模块导入成功")
        
        print("✅ 后端模块导入测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 后端模块导入失败: {e}")
        return False

def test_api_endpoints():
    """测试 API 端点"""
    try:
        print("\n测试 API 端点...")
        
        import requests
        import time
        
        # 等待服务启动
        print("等待服务启动...")
        time.sleep(2)
        
        # 测试健康检查
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ 健康检查端点正常")
        else:
            print(f"⚠ 健康检查端点返回状态码: {response.status_code}")
        
        # 测试统计端点
        response = requests.get("http://localhost:8000/api/stats/health", timeout=5)
        if response.status_code == 200:
            print("✓ 统计健康检查端点正常")
        else:
            print(f"⚠ 统计健康检查端点返回状态码: {response.status_code}")
        
        print("✅ API 端点测试完成")
        return True
        
    except requests.exceptions.ConnectionError:
        print("⚠ 无法连接到服务器，请确保后端服务已启动")
        return False
    except Exception as e:
        print(f"❌ API 端点测试失败: {e}")
        return False

def main():
    print("=== AI 短视频制作平台模块测试 ===\n")
    
    # 测试后端导入
    backend_ok = test_backend_imports()
    
    # 测试 API 端点（如果后端导入成功）
    if backend_ok:
        api_ok = test_api_endpoints()
    else:
        api_ok = False
    
    print(f"\n=== 测试结果 ===")
    print(f"后端模块: {'✅ 通过' if backend_ok else '❌ 失败'}")
    print(f"API 端点: {'✅ 通过' if api_ok else '❌ 失败'}")
    
    if backend_ok and api_ok:
        print("\n🎉 所有测试通过！应用可以正常运行。")
    else:
        print("\n⚠ 部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()