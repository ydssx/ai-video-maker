#!/usr/bin/env python3
"""
简单API测试
"""

import requests

def test_health():
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"健康检查: {response.status_code}")
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            return True
    except:
        print("❌ 后端服务未运行")
        return False

def test_templates():
    try:
        response = requests.get("http://localhost:8000/api/video/templates", timeout=5)
        print(f"模板API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 模板数量: {len(data.get('templates', []))}")
            return True
    except Exception as e:
        print(f"❌ 模板API失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 简单API测试")
    test_health()
    test_templates()