#!/usr/bin/env python3
"""
模板选择器测试脚本
"""

import sys
import os
import requests
import time

def test_template_api():
    """测试模板API"""
    print("🎨 测试模板API...")
    
    try:
        response = requests.get("http://localhost:8000/api/video/templates", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('templates', [])
            
            print(f"✅ API响应正常")
            print(f"📊 模板数量: {len(templates)}")
            
            if templates:
                print("📋 可用模板:")
                for template in templates[:5]:  # 只显示前5个
                    print(f"   - {template.get('id', 'N/A')}: {template.get('name', 'N/A')}")
                
                if len(templates) > 5:
                    print(f"   ... 还有 {len(templates) - 5} 个模板")
            
            return True
        else:
            print(f"❌ API响应错误: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("💡 请确保后端服务已启动: python start.py")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def check_frontend_files():
    """检查前端文件"""
    print("\n📁 检查前端文件...")
    
    files_to_check = [
        "frontend/src/components/TemplateSelector.js",
        "frontend/src/components/VideoPreview.js",
        "frontend/src/App.css"
    ]
    
    results = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            results.append(True)
        else:
            print(f"❌ {file_path} - 文件不存在")
            results.append(False)
    
    return all(results)

def check_css_styles():
    """检查CSS样式"""
    print("\n🎨 检查CSS样式...")
    
    css_file = "frontend/src/App.css"
    
    if not os.path.exists(css_file):
        print("❌ App.css 文件不存在")
        return False
    
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_styles = [
            '.template-card',
            '.template-selected',
            '.template-check',
            '.template-preview',
            '.template-info'
        ]
        
        missing_styles = []
        
        for style in required_styles:
            if style in content:
                print(f"✅ {style}")
            else:
                print(f"❌ {style} - 样式缺失")
                missing_styles.append(style)
        
        return len(missing_styles) == 0
        
    except Exception as e:
        print(f"❌ 检查CSS失败: {str(e)}")
        return False

def generate_debug_info():
    """生成调试信息"""
    print("\n🔍 生成调试信息...")
    
    debug_info = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "issues_found": [],
        "suggestions": []
    }
    
    # 检查常见问题
    template_file = "frontend/src/components/TemplateSelector.js"
    if os.path.exists(template_file):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查点击事件
            if 'onClick=' in content:
                print("✅ 找到onClick事件处理")
            else:
                debug_info["issues_found"].append("缺少onClick事件处理")
                debug_info["suggestions"].append("添加onClick事件到Card组件")
            
            # 检查函数传递
            if 'onTemplateChange' in content:
                print("✅ 找到onTemplateChange函数调用")
            else:
                debug_info["issues_found"].append("缺少onTemplateChange函数调用")
                debug_info["suggestions"].append("确保正确调用onTemplateChange函数")
            
            # 检查状态管理
            if 'selectedTemplate' in content:
                print("✅ 找到selectedTemplate状态")
            else:
                debug_info["issues_found"].append("缺少selectedTemplate状态")
                debug_info["suggestions"].append("添加selectedTemplate状态管理")
                
        except Exception as e:
            debug_info["issues_found"].append(f"文件读取错误: {str(e)}")
    
    return debug_info

def main():
    """主测试函数"""
    print("🚀 开始模板选择器问题诊断")
    print("=" * 50)
    
    results = {}
    
    # 运行测试
    results["模板API"] = test_template_api()
    results["前端文件"] = check_frontend_files()
    results["CSS样式"] = check_css_styles()
    
    # 生成调试信息
    debug_info = generate_debug_info()
    
    # 生成报告
    print("\n" + "=" * 50)
    print("📊 诊断报告")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"总检查项: {total_tests}")
    print(f"通过检查: {passed_tests}")
    print(f"失败检查: {total_tests - passed_tests}")
    
    print("\n详细结果:")
    for test_name, result in results.items():
        status = "✅ 正常" if result else "❌ 异常"
        print(f"  {test_name}: {status}")
    
    if debug_info["issues_found"]:
        print(f"\n🔍 发现的问题:")
        for issue in debug_info["issues_found"]:
            print(f"  - {issue}")
    
    if debug_info["suggestions"]:
        print(f"\n💡 修复建议:")
        for suggestion in debug_info["suggestions"]:
            print(f"  - {suggestion}")
    
    print(f"\n🎯 下一步行动:")
    if not results["模板API"]:
        print("  1. 启动后端服务: python start.py")
    if not results["前端文件"]:
        print("  2. 检查前端文件完整性")
    if not results["CSS样式"]:
        print("  3. 添加缺失的CSS样式")
    
    print("  4. 在浏览器开发者工具中检查JavaScript错误")
    print("  5. 确认点击事件是否被其他元素阻挡")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)