#!/usr/bin/env python3
"""
测试视频下载功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_video_download():
    """测试视频下载功能"""
    print("🎬 测试视频下载功能...")
    
    try:
        # 1. 创建测试视频
        print("创建测试视频...")
        response = requests.post(f"{BASE_URL}/api/video/create-test-video")
        
        if response.status_code == 200:
            result = response.json()
            video_id = result.get('video_id')
            
            if video_id:
                print(f"✅ 测试视频创建成功，ID: {video_id}")
                
                # 2. 检查视频状态
                print("检查视频状态...")
                status_response = requests.get(f"{BASE_URL}/api/video/status/{video_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"✅ 视频状态: {status_data.get('status')}")
                    print(f"   下载链接: {status_data.get('download_url')}")
                    
                    if status_data.get('cloud_download_url'):
                        print(f"   云端链接: {status_data.get('cloud_download_url')}")
                    
                    # 3. 测试下载
                    print("测试下载功能...")
                    download_response = requests.get(f"{BASE_URL}/api/video/download/{video_id}")
                    
                    if download_response.status_code == 200:
                        print("✅ 下载链接可访问")
                        print(f"   Content-Type: {download_response.headers.get('content-type')}")
                        print(f"   Content-Length: {download_response.headers.get('content-length', 'Unknown')}")
                        return True
                    else:
                        print(f"❌ 下载失败: {download_response.status_code}")
                        return False
                else:
                    print(f"❌ 状态查询失败: {status_response.status_code}")
                    return False
            else:
                print("❌ 视频ID为空")
                return False
        else:
            print(f"❌ 创建测试视频失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False

def test_api_endpoints():
    """测试相关API端点"""
    print("\n🔍 测试API端点...")
    
    endpoints = [
        "/health",
        "/api/video/templates",
        "/api/video/voices"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint} - 正常")
            else:
                print(f"❌ {endpoint} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - 错误: {e}")

def main():
    print("🚀 视频下载功能测试")
    print("=" * 40)
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试视频下载
    success = test_video_download()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 视频下载功能测试通过！")
        print("\n使用说明:")
        print("1. 启动应用: python start.py")
        print("2. 访问: http://localhost:3000")
        print("3. 生成脚本并制作视频")
        print("4. 视频完成后可以看到下载按钮")
    else:
        print("❌ 视频下载功能测试失败")
        print("\n请检查:")
        print("1. 后端服务是否正常运行")
        print("2. FFmpeg是否正确安装")
        print("3. 输出目录是否有写入权限")

if __name__ == "__main__":
    main()