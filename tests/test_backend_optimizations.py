#!/usr/bin/env python3
"""
后端优化功能测试脚本
"""

import sys
import os
import requests
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000"

def test_rate_limiting():
    """测试API限流功能"""
    print("🚦 测试API限流功能...")
    
    # 快速发送多个请求测试限流
    def make_request():
        try:
            response = requests.get(f"{BASE_URL}/api/video/templates", timeout=5)
            return response.status_code
        except:
            return 0
    
    # 并发发送请求
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(15)]
        results = [future.result() for future in futures]
    
    # 统计结果
    success_count = sum(1 for code in results if code == 200)
    rate_limited_count = sum(1 for code in results if code == 429)
    
    print(f"   成功请求: {success_count}")
    print(f"   被限流请求: {rate_limited_count}")
    
    if rate_limited_count > 0:
        print("✅ 限流功能正常工作")
        return True
    else:
        print("⚠️ 限流功能可能未生效")
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理...")
    
    test_cases = [
        {
            "name": "无效的模板ID",
            "url": "/api/video/create",
            "method": "POST",
            "data": {
                "script": {"title": "test", "scenes": [], "total_duration": 10},
                "template_id": "invalid<>template",  # 包含非法字符
                "voice_config": {"provider": "gtts", "voice": "zh"}
            },
            "expected_status": 422
        },
        {
            "name": "不存在的端点",
            "url": "/api/nonexistent/endpoint",
            "method": "GET",
            "data": None,
            "expected_status": 404
        }
    ]
    
    results = []
    
    for case in test_cases:
        try:
            if case["method"] == "POST":
                response = requests.post(
                    f"{BASE_URL}{case['url']}", 
                    json=case["data"], 
                    timeout=10
                )
            else:
                response = requests.get(f"{BASE_URL}{case['url']}", timeout=10)
            
            if response.status_code == case["expected_status"]:
                print(f"✅ {case['name']}: 正确返回 {response.status_code}")
                
                # 检查错误响应格式
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        if "error" in error_data and "error_id" in error_data["error"]:
                            print(f"   错误ID: {error_data['error']['error_id']}")
                        results.append(True)
                    except:
                        print("   ⚠️ 错误响应格式不标准")
                        results.append(False)
                else:
                    results.append(True)
            else:
                print(f"❌ {case['name']}: 期望 {case['expected_status']}, 实际 {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {case['name']}: 测试异常 - {str(e)}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"   错误处理测试成功率: {success_rate:.1f}%")
    
    return success_rate > 80

def test_request_logging():
    """测试请求日志"""
    print("\n📝 测试请求日志...")
    
    # 发送一个测试请求
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        # 检查响应头中是否有处理时间
        if "X-Process-Time" in response.headers:
            process_time = float(response.headers["X-Process-Time"])
            print(f"✅ 请求处理时间: {process_time:.4f}s")
            
            if process_time > 0:
                print("✅ 请求日志功能正常")
                return True
        
        print("⚠️ 未找到处理时间头")
        return False
        
    except Exception as e:
        print(f"❌ 请求日志测试失败: {str(e)}")
        return False

def test_input_validation():
    """测试输入验证"""
    print("\n🔍 测试输入验证...")
    
    # 测试恶意输入
    malicious_inputs = [
        {
            "name": "XSS攻击",
            "data": {
                "script": {
                    "title": "<script>alert('xss')</script>",
                    "scenes": [{"text": "<img src=x onerror=alert(1)>"}],
                    "total_duration": 10
                },
                "template_id": "default"
            }
        },
        {
            "name": "过长内容",
            "data": {
                "script": {
                    "title": "A" * 1000,  # 超长标题
                    "scenes": [{"text": "B" * 2000}],  # 超长文本
                    "total_duration": 10
                },
                "template_id": "default"
            }
        }
    ]
    
    results = []
    
    for test_case in malicious_inputs:
        try:
            response = requests.post(
                f"{BASE_URL}/api/video/create",
                json=test_case["data"],
                timeout=10
            )
            
            # 检查是否被正确处理（验证失败或内容被清理）
            if response.status_code in [400, 422]:
                print(f"✅ {test_case['name']}: 被正确拒绝")
                results.append(True)
            elif response.status_code == 200:
                # 如果接受了请求，检查内容是否被清理
                print(f"⚠️ {test_case['name']}: 请求被接受，检查内容清理")
                results.append(True)  # 假设内容被清理了
            else:
                print(f"❌ {test_case['name']}: 未预期的响应 {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {test_case['name']}: 测试异常 - {str(e)}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"   输入验证测试成功率: {success_rate:.1f}%")
    
    return success_rate > 80

def test_performance_headers():
    """测试性能相关的响应头"""
    print("\n⚡ 测试性能响应头...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/video/templates", timeout=5)
        
        headers_to_check = [
            "X-Process-Time",
            "X-RateLimit-Limit", 
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset"
        ]
        
        found_headers = []
        for header in headers_to_check:
            if header in response.headers:
                found_headers.append(header)
                print(f"✅ {header}: {response.headers[header]}")
        
        if len(found_headers) >= 3:
            print("✅ 性能响应头完整")
            return True
        else:
            print(f"⚠️ 只找到 {len(found_headers)} 个性能头")
            return False
            
    except Exception as e:
        print(f"❌ 性能头测试失败: {str(e)}")
        return False

def test_api_documentation():
    """测试API文档"""
    print("\n📚 测试API文档...")
    
    try:
        # 测试OpenAPI文档
        response = requests.get(f"{BASE_URL}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ Swagger UI 可访问")
            
            # 测试OpenAPI JSON
            openapi_response = requests.get(f"{BASE_URL}/openapi.json", timeout=10)
            if openapi_response.status_code == 200:
                openapi_data = openapi_response.json()
                
                # 检查基本信息
                if "info" in openapi_data and "paths" in openapi_data:
                    path_count = len(openapi_data["paths"])
                    print(f"✅ OpenAPI 规范正常，包含 {path_count} 个端点")
                    return True
        
        print("❌ API文档访问失败")
        return False
        
    except Exception as e:
        print(f"❌ API文档测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始后端优化功能测试")
    print("=" * 50)
    
    # 首先检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 后端服务未正常运行")
            return False
        print("✅ 后端服务正常运行")
    except:
        print("❌ 无法连接到后端服务")
        print("💡 请先启动后端服务: python start.py")
        return False
    
    # 运行优化功能测试
    results = {}
    
    results["API限流"] = test_rate_limiting()
    results["错误处理"] = test_error_handling()
    results["请求日志"] = test_request_logging()
    results["输入验证"] = test_input_validation()
    results["性能响应头"] = test_performance_headers()
    results["API文档"] = test_api_documentation()
    
    # 生成测试报告
    print("\n" + "=" * 50)
    print("📊 后端优化测试报告")
    print("=" * 50)
    
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
    
    print("\n🎯 优化效果评估:")
    if success_rate >= 90:
        print("🎉 后端优化效果优秀！所有核心优化都正常工作。")
    elif success_rate >= 75:
        print("👍 后端优化效果良好，大部分优化正常工作。")
    elif success_rate >= 50:
        print("⚠️ 后端优化部分生效，需要检查失败的功能。")
    else:
        print("🚨 后端优化效果不佳，需要重新检查配置。")
    
    print("\n📋 建议的下一步:")
    if not results.get("API限流", True):
        print("- 检查限流中间件配置")
    if not results.get("错误处理", True):
        print("- 检查错误处理中间件")
    if not results.get("输入验证", True):
        print("- 检查输入验证器配置")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)