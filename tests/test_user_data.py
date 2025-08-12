#!/usr/bin/env python3
"""
测试用户数据功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_user_data_apis():
    """测试用户数据API"""
    print("🧪 测试用户数据API...")
    
    endpoints = [
        ("GET", "/api/user-data/stats", "用户统计"),
        ("GET", "/api/user-data/quota", "用户配额"),
        ("GET", "/api/user-data/dashboard", "仪表板数据"),
        ("GET", "/api/user-data/activity", "用户活动"),
        ("POST", "/api/user-data/record-script", "记录脚本生成"),
        ("POST", "/api/user-data/record-video", "记录视频创建")
    ]
    
    results = {}
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", 
                                       json={"duration": 60}, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {description}: {endpoint}")
                results[endpoint] = True
                
                # 显示部分响应数据
                try:
                    data = response.json()
                    if 'stats' in data:
                        stats = data['stats']
                        print(f"   脚本: {stats.get('scripts_generated', 0)}, 视频: {stats.get('videos_created', 0)}")
                    elif 'quota' in data:
                        quota = data['quota']
                        print(f"   今日脚本: {quota.get('used_today_scripts', 0)}/{quota.get('daily_scripts', 10)}")
                except:
                    pass
                    
            else:
                print(f"❌ {description}: {endpoint} - 状态码 {response.status_code}")
                results[endpoint] = False
                
        except Exception as e:
            print(f"❌ {description}: {endpoint} - 错误: {e}")
            results[endpoint] = False
    
    return results

def main():
    print("🚀 用户数据功能测试")
    print("=" * 40)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常")
        else:
            print("❌ 后端服务异常")
            return
    except:
        print("❌ 无法连接到后端服务")
        print("请确保运行了: python start.py")
        return
    
    # 测试API端点
    api_results = test_user_data_apis()
    
    # 总结
    print("\n" + "=" * 40)
    print("📊 测试结果:")
    
    api_success = sum(api_results.values())
    api_total = len(api_results)
    
    print(f"API测试: {api_success}/{api_total} 通过")
    
    if api_success == api_total:
        print("\n🎉 所有测试通过！用户数据功能正常")
    else:
        print("\n❌ 部分测试失败，请检查相关功能")

if __name__ == "__main__":
    main()