#!/usr/bin/env python3
"""
AI 短视频制作平台功能测试脚本
"""

import requests
import json
import time
import os
from pathlib import Path

# 配置
BASE_URL = "http://localhost:8000"
TEST_DATA_DIR = Path("test_data")
TEST_DATA_DIR.mkdir(exist_ok=True)

def test_api_health():
    """测试 API 健康状态"""
    print("🔍 测试 API 健康状态...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API 服务正常")
            return True
        else:
            print(f"❌ API 服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到 API 服务: {e}")
        return False

def test_script_generation():
    """测试脚本生成功能"""
    print("\n🎬 测试脚本生成功能...")
    
    test_data = {
        "topic": "人工智能的发展历程",
        "duration": 60,
        "style": "educational",
        "target_audience": "general"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/script/generate", json=test_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("script"):
                print("✅ 脚本生成成功")
                print(f"   场景数量: {len(result['script']['scenes'])}")
                print(f"   总时长: {result['script']['total_duration']}秒")
                
                # 保存测试脚本
                with open(TEST_DATA_DIR / "test_script.json", "w", encoding="utf-8") as f:
                    json.dump(result["script"], f, ensure_ascii=False, indent=2)
                
                return result["script"]
            else:
                print("❌ 脚本生成失败: 响应格式错误")
                return None
        else:
            print(f"❌ 脚本生成失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 脚本生成异常: {e}")
        return None

def test_template_list():
    """测试模板列表功能"""
    print("\n🎨 测试模板列表功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/video/templates")
        if response.status_code == 200:
            result = response.json()
            if result.get("templates"):
                print("✅ 模板列表获取成功")
                print(f"   模板数量: {len(result['templates'])}")
                for template in result["templates"][:3]:  # 显示前3个模板
                    print(f"   - {template.get('name', 'Unknown')}")
                return result["templates"]
            else:
                print("❌ 模板列表为空")
                return []
        else:
            print(f"❌ 模板列表获取失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 模板列表获取异常: {e}")
        return []

def test_video_creation(script):
    """测试视频创建功能"""
    if not script:
        print("\n❌ 跳过视频创建测试: 没有可用脚本")
        return None
    
    print("\n🎥 测试视频创建功能...")
    
    test_data = {
        "script": script,
        "template_id": "default",
        "voice_config": {
            "provider": "gtts",
            "voice": "zh",
            "speed": 1.0,
            "enabled": True
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/video/create", json=test_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("video_id"):
                print("✅ 视频创建任务提交成功")
                print(f"   视频ID: {result['video_id']}")
                return result["video_id"]
            else:
                print("❌ 视频创建失败: 没有返回视频ID")
                return None
        else:
            print(f"❌ 视频创建失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 视频创建异常: {e}")
        return None

def test_video_status(video_id):
    """测试视频状态查询"""
    if not video_id:
        print("\n❌ 跳过视频状态测试: 没有视频ID")
        return
    
    print(f"\n📊 测试视频状态查询 (ID: {video_id})...")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/api/video/status/{video_id}")
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "unknown")
                print(f"   尝试 {attempt + 1}: 状态 = {status}")
                
                if status == "completed":
                    print("✅ 视频制作完成")
                    return True
                elif status == "failed":
                    print("❌ 视频制作失败")
                    return False
                elif status in ["processing", "pending"]:
                    time.sleep(2)  # 等待2秒后重试
                    continue
                else:
                    print(f"⚠️ 未知状态: {status}")
                    return False
            else:
                print(f"❌ 状态查询失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 状态查询异常: {e}")
            return False
    
    print("⏰ 视频制作超时")
    return False

def test_project_management():
    """测试项目管理功能"""
    print("\n📁 测试项目管理功能...")
    
    # 创建测试项目
    project_data = {
        "name": "测试项目",
        "description": "这是一个自动化测试项目",
        "category": "general",
        "tags": ["test", "automation"],
        "script": {
            "scenes": [
                {"text": "这是测试场景", "duration": 5}
            ],
            "total_duration": 5
        },
        "video_config": {}
    }
    
    try:
        # 保存项目
        response = requests.post(f"{BASE_URL}/api/projects/save", json=project_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("project"):
                project_id = result["project"]["id"]
                print("✅ 项目保存成功")
                print(f"   项目ID: {project_id}")
                
                # 获取项目列表
                response = requests.get(f"{BASE_URL}/api/projects/list")
                if response.status_code == 200:
                    result = response.json()
                    if result.get("projects"):
                        print("✅ 项目列表获取成功")
                        print(f"   项目数量: {len(result['projects'])}")
                    else:
                        print("❌ 项目列表为空")
                
                # 删除测试项目
                response = requests.delete(f"{BASE_URL}/api/projects/{project_id}")
                if response.status_code == 200:
                    print("✅ 测试项目删除成功")
                else:
                    print("⚠️ 测试项目删除失败")
                
                return True
            else:
                print("❌ 项目保存失败: 响应格式错误")
                return False
        else:
            print(f"❌ 项目保存失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 项目管理测试异常: {e}")
        return False

def test_user_assets():
    """测试用户素材管理功能"""
    print("\n🖼️ 测试用户素材管理功能...")
    
    try:
        # 获取素材列表
        response = requests.get(f"{BASE_URL}/api/user-assets/list")
        if response.status_code == 200:
            result = response.json()
            print("✅ 素材列表获取成功")
            print(f"   素材数量: {len(result.get('assets', []))}")
            return True
        else:
            print(f"❌ 素材列表获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 素材管理测试异常: {e}")
        return False

def test_audio_management():
    """测试音频管理功能"""
    print("\n🎵 测试音频管理功能...")
    
    try:
        # 获取音频文件列表
        response = requests.get(f"{BASE_URL}/api/audio/list")
        if response.status_code == 200:
            result = response.json()
            print("✅ 音频列表获取成功")
            print(f"   音频文件数量: {len(result.get('audio_files', []))}")
            return True
        else:
            print(f"❌ 音频列表获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 音频管理测试异常: {e}")
        return False

def test_statistics():
    """测试统计功能"""
    print("\n📈 测试统计功能...")
    
    try:
        # 获取项目统计
        response = requests.get(f"{BASE_URL}/api/projects/stats/overview")
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("stats"):
                stats = result["stats"]
                print("✅ 项目统计获取成功")
                print(f"   总项目数: {stats.get('total_projects', 0)}")
                print(f"   分类统计: {stats.get('category_stats', {})}")
                return True
            else:
                print("❌ 统计数据格式错误")
                return False
        else:
            print(f"❌ 统计数据获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 统计功能测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始 AI 短视频制作平台功能测试\n")
    
    # 测试结果统计
    test_results = {}
    
    # 1. 测试 API 健康状态
    test_results["API健康"] = test_api_health()
    
    if not test_results["API健康"]:
        print("\n❌ API 服务不可用，停止测试")
        return
    
    # 2. 测试脚本生成
    script = test_script_generation()
    test_results["脚本生成"] = script is not None
    
    # 3. 测试模板列表
    templates = test_template_list()
    test_results["模板列表"] = len(templates) > 0
    
    # 4. 测试视频创建（可选，因为可能需要很长时间）
    # video_id = test_video_creation(script)
    # test_results["视频创建"] = video_id is not None
    
    # 5. 测试项目管理
    test_results["项目管理"] = test_project_management()
    
    # 6. 测试用户素材
    test_results["素材管理"] = test_user_assets()
    
    # 7. 测试音频管理
    test_results["音频管理"] = test_audio_management()
    
    # 8. 测试统计功能
    test_results["统计功能"] = test_statistics()
    
    # 输出测试结果
    print("\n" + "="*50)
    print("📋 测试结果汇总")
    print("="*50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:12} : {status}")
        if result:
            passed += 1
    
    print("-"*50)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！平台功能正常")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()