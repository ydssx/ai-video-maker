#!/usr/bin/env python3
"""
增强后端功能测试脚本
测试新增的服务和API端点
"""

import sys
import os
import asyncio
import requests
import json
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000"

def test_system_health():
    """测试系统健康检查"""
    print("🏥 测试系统健康检查...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/system/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ 系统健康检查通过")
            print(f"   状态: {health_data.get('status', 'unknown')}")
            
            # 检查各个组件状态
            components = ['database', 'storage', 'ai_service', 'video_service']
            for component in components:
                if component in health_data:
                    status = health_data[component].get('status', 'unknown')
                    print(f"   {component}: {status}")
            
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        return False
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

def test_system_stats():
    """测试系统统计信息"""
    print("\n📊 测试系统统计信息...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/system/stats", timeout=10)
        
        if response.status_code == 200:
            stats_data = response.json()
            print("✅ 系统统计获取成功")
            
            # 显示统计信息
            if 'database' in stats_data:
                db_stats = stats_data['database']
                print(f"   数据库 - 用户: {db_stats.get('total_users', 0)}, 项目: {db_stats.get('total_projects', 0)}")
            
            if 'storage' in stats_data:
                storage_stats = stats_data['storage']
                print(f"   存储 - 文件: {storage_stats.get('total_files', 0)}, 大小: {storage_stats.get('total_size', 0)} bytes")
            
            return True
        else:
            print(f"❌ 统计信息获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 统计信息测试异常: {str(e)}")
        return False

def test_performance_metrics():
    """测试性能指标"""
    print("\n⚡ 测试性能指标...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/system/performance", timeout=10)
        
        if response.status_code == 200:
            perf_data = response.json()
            print("✅ 性能指标获取成功")
            
            # 显示性能信息
            if 'cpu' in perf_data:
                cpu_info = perf_data['cpu']
                print(f"   CPU: {cpu_info.get('percent', 0):.1f}% ({cpu_info.get('count', 0)} 核)")
            
            if 'memory' in perf_data:
                memory_info = perf_data['memory']
                memory_gb = memory_info.get('total', 0) / (1024**3)
                print(f"   内存: {memory_info.get('percent', 0):.1f}% ({memory_gb:.1f}GB 总计)")
            
            return True
        else:
            print(f"❌ 性能指标获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 性能指标测试异常: {str(e)}")
        return False

def test_ai_service_endpoints():
    """测试AI服务端点"""
    print("\n🤖 测试AI服务端点...")
    
    # 测试脚本生成
    try:
        script_data = {
            "topic": "测试主题",
            "style": "educational",
            "duration": "30s",
            "language": "zh"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/script/generate",
            json=script_data,
            timeout=30
        )
        
        if response.status_code == 200:
            script_result = response.json()
            print("✅ AI脚本生成成功")
            print(f"   标题: {script_result.get('title', 'N/A')}")
            print(f"   场景数: {len(script_result.get('scenes', []))}")
            return True
        else:
            print(f"❌ AI脚本生成失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ AI服务测试异常: {str(e)}")
        return False

def test_video_templates():
    """测试视频模板"""
    print("\n🎨 测试视频模板...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/video/templates", timeout=10)
        
        if response.status_code == 200:
            templates_data = response.json()
            templates = templates_data.get('templates', [])
            print(f"✅ 视频模板获取成功，共 {len(templates)} 个模板")
            
            # 显示模板分类统计
            categories = {}
            for template in templates:
                category = template.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            print("   模板分类:")
            for category, count in categories.items():
                print(f"     {category}: {count} 个")
            
            return True
        else:
            print(f"❌ 视频模板获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 视频模板测试异常: {str(e)}")
        return False

def test_voice_options():
    """测试语音选项"""
    print("\n🎵 测试语音选项...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/video/voices", timeout=10)
        
        if response.status_code == 200:
            voices_data = response.json()
            voices = voices_data.get('voices', {})
            print("✅ 语音选项获取成功")
            
            # 显示语音引擎统计
            for engine, voice_list in voices.items():
                print(f"   {engine}: {len(voice_list)} 个语音")
            
            return True
        else:
            print(f"❌ 语音选项获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 语音选项测试异常: {str(e)}")
        return False

def test_user_management():
    """测试用户管理"""
    print("\n👤 测试用户管理...")
    
    try:
        # 测试用户注册
        user_data = {
            "username": f"test_user_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "test_password_123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/users/register",
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            user_result = response.json()
            print("✅ 用户注册成功")
            print(f"   用户ID: {user_result.get('id')}")
            print(f"   用户名: {user_result.get('username')}")
            
            # 测试用户统计
            user_id = user_result.get('id')
            if user_id:
                stats_response = requests.get(
                    f"{BASE_URL}/api/users/stats/{user_id}",
                    timeout=10
                )
                
                if stats_response.status_code == 200:
                    print("✅ 用户统计获取成功")
                else:
                    print(f"⚠️ 用户统计获取失败: {stats_response.status_code}")
            
            return True
        else:
            print(f"❌ 用户注册失败: {response.status_code}")
            if response.text:
                print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 用户管理测试异常: {str(e)}")
        return False

def test_system_cleanup():
    """测试系统清理"""
    print("\n🧹 测试系统清理...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/system/cleanup", timeout=30)
        
        if response.status_code == 200:
            cleanup_result = response.json()
            print("✅ 系统清理成功")
            
            results = cleanup_result.get('results', {})
            for key, value in results.items():
                print(f"   {key}: {value}")
            
            return True
        else:
            print(f"❌ 系统清理失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 系统清理测试异常: {str(e)}")
        return False

def test_api_documentation():
    """测试API文档"""
    print("\n📚 测试API文档...")
    
    try:
        # 测试OpenAPI文档
        response = requests.get(f"{BASE_URL}/docs", timeout=10)
        
        if response.status_code == 200:
            print("✅ API文档可访问")
            return True
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API文档测试异常: {str(e)}")
        return False

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("📊 增强后端功能测试报告")
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
    
    print("\n🎯 功能状态评估:")
    if success_rate >= 90:
        print("🎉 后端功能优秀！所有核心功能正常工作。")
    elif success_rate >= 75:
        print("👍 后端功能良好，大部分功能正常，建议修复失败项。")
    elif success_rate >= 50:
        print("⚠️ 后端功能基本可用，但需要重点关注失败的功能。")
    else:
        print("🚨 后端功能存在严重问题，需要立即修复。")
    
    print("\n📋 建议的下一步行动:")
    if not results.get("系统健康检查", True):
        print("- 检查系统服务状态和依赖项")
    if not results.get("AI服务端点", True):
        print("- 检查AI服务配置和API密钥")
    if not results.get("用户管理", True):
        print("- 检查数据库连接和用户表结构")
    if success_rate < 100:
        print("- 查看详细错误日志进行问题排查")
        print("- 确保所有必要的依赖项已安装")
    
    return success_rate >= 75

def main():
    """主测试函数"""
    print("🚀 开始增强后端功能测试")
    print("=" * 60)
    
    # 运行所有测试
    results = {}
    
    results["系统健康检查"] = test_system_health()
    results["系统统计信息"] = test_system_stats()
    results["性能指标"] = test_performance_metrics()
    results["AI服务端点"] = test_ai_service_endpoints()
    results["视频模板"] = test_video_templates()
    results["语音选项"] = test_voice_options()
    results["用户管理"] = test_user_management()
    results["系统清理"] = test_system_cleanup()
    results["API文档"] = test_api_documentation()
    
    # 生成测试报告
    success = generate_test_report(results)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)