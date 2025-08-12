#!/usr/bin/env python3
"""
测试API路由是否正确配置
"""

import sys
import os
sys.path.append('backend')

def test_routes():
    """测试路由配置"""
    print("🔍 测试API路由配置...")
    
    try:
        from fastapi import FastAPI
        from routers import video_maker
        
        # 创建测试应用
        app = FastAPI()
        app.include_router(video_maker.router, prefix="/api/video", tags=["video"])
        
        # 获取所有路由
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                for method in route.methods:
                    if method != 'HEAD':  # 忽略HEAD方法
                        routes.append(f"{method} {route.path}")
        
        print("✅ 发现的API路由:")
        for route in sorted(routes):
            print(f"   {route}")
        
        # 检查关键路由
        required_routes = [
            "POST /api/video/create",
            "GET /api/video/status/{video_id}",
            "GET /api/video/download/{video_id}",
            "GET /api/video/templates",
            "GET /api/video/voices"
        ]
        
        missing_routes = []
        for required_route in required_routes:
            found = False
            for route in routes:
                if required_route.replace("{video_id}", "{video_id}") in route:
                    found = True
                    break
            if not found:
                missing_routes.append(required_route)
        
        if missing_routes:
            print(f"\n❌ 缺失的路由:")
            for route in missing_routes:
                print(f"   {route}")
            return False
        else:
            print(f"\n✅ 所有必需的路由都已配置")
            return True
            
    except Exception as e:
        print(f"❌ 路由测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """测试导入是否正常"""
    print("\n📦 测试模块导入...")
    
    try:
        from routers import video_maker
        print("✅ video_maker 导入成功")
        
        from models import VideoRequest, VideoResponse
        print("✅ 模型导入成功")
        
        from services.ai_service import ai_service
        print("✅ AI服务导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def main():
    print("🚀 API路由测试")
    print("=" * 40)
    
    # 测试导入
    import_ok = test_imports()
    
    # 测试路由
    routes_ok = test_routes()
    
    print("\n" + "=" * 40)
    if import_ok and routes_ok:
        print("🎉 所有测试通过！API路由配置正确")
        print("\n现在可以启动服务:")
        print("python start.py")
    else:
        print("❌ 测试失败，请检查配置")

if __name__ == "__main__":
    main()