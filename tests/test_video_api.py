#!/usr/bin/env python3
"""
视频API测试脚本
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_video_create_api():
    """测试视频创建API"""
    print("🎬 测试视频创建API...")
    
    # 模拟前端发送的数据
    test_data = {
        "script": {
            "title": "测试视频",
            "scenes": [
                {
                    "text": "这是第一个场景",
                    "duration": 5.0,
                    "image_keywords": ["测试", "场景"],
                    "transition": "fade"
                },
                {
                    "text": "这是第二个场景", 
                    "duration": 5.0,
                    "image_keywords": ["测试", "场景2"],
                    "transition": "slide"
                }
            ],
            "total_duration": 10.0,
            "style": "educational"
        },
        "template_id": "default",
        "voice_config": {
            "provider": "gtts",
            "voice": "zh",
            "speed": 1.0,
            "enabled": True
        },
        "text_style": {
            "fontFamily": "Arial",
            "fontSize": 48,
            "fontColor": "#ffffff",
            "position": "center"
        },
        "export_config": {
            "resolution": "720p",
            "fps": 30,
            "format": "mp4",
            "quality": "high"
        }
    }
    
    try:
        # 发送创建请求
        response = requests.post(
            f"{BASE_URL}/api/video/create",
            json=test_data,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            video_id = result.get('video_id')
            print(f"✅ 视频创建请求成功")
            print(f"   视频ID: {video_id}")
            print(f"   状态: {result.get('status')}")
            
            # 测试状态查询
            if video_id:
                print(f"\n📊 查询视频状态...")
                for i in range(5):
                    time.sleep(2)
                    status_response = requests.get(
                        f"{BASE_URL}/api/video/status/{video_id}",
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   状态查询 {i+1}: {status_data.get('status')}")
                        
                        if status_data.get('status') in ['completed', 'failed']:
                            break
                    else:
                        print(f"   状态查询失败: {status_response.status_code}")
            
            return True
        else:
            print(f"❌ 视频创建请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("💡 请确保后端服务正在运行: python start.py")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def test_video_templates():
    """测试视频模板API"""
    print("\n🎨 测试视频模板API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/video/templates", timeout=10)
        
        if response.status_code == 200:
            templates_data = response.json()
            templates = templates_data.get('templates', [])
            print(f"✅ 模板获取成功，共 {len(templates)} 个模板")
            
            # 显示前3个模板
            for i, template in enumerate(templates[:3]):
                print(f"   {i+1}. {template.get('name')} ({template.get('category')})")
            
            return True
        else:
            print(f"❌ 模板获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 模板测试异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始视频API测试")
    print("=" * 40)
    
    results = {}
    results["视频创建API"] = test_video_create_api()
    results["视频模板API"] = test_video_templates()
    
    # 生成报告
    print("\n" + "=" * 40)
    print("📊 测试报告")
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
        print("\n🎉 所有测试通过！视频API工作正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查后端服务状态。")
    
    return success_rate == 100

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)