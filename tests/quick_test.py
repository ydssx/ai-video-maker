#!/usr/bin/env python3
"""
快速测试视频制作功能
"""

import requests
import json
import time

def test_video_creation():
    """测试视频创建"""
    print("🎬 快速测试视频创建...")
    
    # 简单的测试脚本
    test_script = {
        "scenes": [
            {
                "text": "这是第一个测试场景",
                "duration": 3,
                "image_keywords": ["test", "scene"]
            },
            {
                "text": "这是第二个测试场景，用来验证文字图层生成功能是否正常工作",
                "duration": 3,
                "image_keywords": ["test", "video"]
            }
        ],
        "total_duration": 6
    }
    
    # 视频请求
    video_request = {
        "script": test_script,
        "template_id": "default",
        "voice_config": {
            "provider": "gtts",
            "voice": "zh",
            "speed": 1.0,
            "enabled": False  # 禁用语音以加快测试
        }
    }
    
    try:
        print("发送视频创建请求...")
        response = requests.post(
            "http://localhost:8000/api/video/create",
            json=video_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            video_id = result.get('video_id')
            print(f"✅ 视频创建请求成功，ID: {video_id}")
            
            # 监控视频状态
            print("监控视频制作进度...")
            for i in range(30):  # 最多等待30次
                time.sleep(2)
                
                status_response = requests.get(f"http://localhost:8000/api/video/status/{video_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    print(f"进度检查 {i+1}: {status}")
                    
                    if status == 'completed':
                        print("🎉 视频制作完成！")
                        return True
                    elif status == 'failed':
                        print("❌ 视频制作失败")
                        return False
                else:
                    print(f"状态查询失败: {status_response.status_code}")
            
            print("⏰ 视频制作超时")
            return False
            
        else:
            print(f"❌ 视频创建请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False

def main():
    print("🚀 快速视频制作测试")
    print("=" * 30)
    
    # 检查服务是否运行
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常")
        else:
            print("❌ 后端服务异常")
            return
    except:
        print("❌ 无法连接到后端服务")
        print("请确保运行了: python start.py")
        return
    
    # 测试视频创建
    success = test_video_creation()
    
    print("\n" + "=" * 30)
    if success:
        print("🎉 测试通过！文字图层问题已修复")
    else:
        print("❌ 测试失败，请检查后端日志")
        print("\n调试建议:")
        print("1. 检查后端控制台输出")
        print("2. 运行: python test_text_image.py")
        print("3. 确保Pillow正确安装")

if __name__ == "__main__":
    main()