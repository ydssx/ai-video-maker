#!/usr/bin/env python3
"""
优化功能测试脚本
测试新增的状态管理、加载指示器、步骤导航等功能
"""

import sys
import os
import time
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_frontend_components():
    """测试前端组件文件"""
    print("🧩 测试前端组件...")
    
    frontend_path = Path("frontend/src")
    
    # 新增的组件文件
    new_components = [
        "contexts/AppContext.js",
        "components/LoadingIndicator.js",
        "components/StepNavigation.js",
        "components/QuickActions.js"
    ]
    
    results = []
    
    for component in new_components:
        component_path = frontend_path / component
        if component_path.exists():
            print(f"✅ {component}")
            
            # 检查文件内容
            try:
                with open(component_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 基本语法检查
                if 'import React' in content:
                    print(f"   ✓ React导入正常")
                else:
                    print(f"   ⚠️ 可能缺少React导入")
                
                if 'export' in content:
                    print(f"   ✓ 导出语句正常")
                else:
                    print(f"   ⚠️ 可能缺少导出语句")
                
                results.append(True)
                
            except Exception as e:
                print(f"   ❌ 文件读取错误: {str(e)}")
                results.append(False)
        else:
            print(f"❌ {component} - 文件不存在")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 组件文件测试成功率: {success_rate:.1f}%")
    
    return success_rate > 80

def test_context_structure():
    """测试Context结构"""
    print("\n🔄 测试Context结构...")
    
    context_file = Path("frontend/src/contexts/AppContext.js")
    
    if not context_file.exists():
        print("❌ AppContext.js 文件不存在")
        return False
    
    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键结构
        checks = [
            ("createContext", "Context创建"),
            ("useReducer", "Reducer使用"),
            ("ActionTypes", "Action类型定义"),
            ("appReducer", "Reducer函数"),
            ("AppProvider", "Provider组件"),
            ("useAppContext", "自定义Hook"),
            ("initialState", "初始状态")
        ]
        
        results = []
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
                results.append(True)
            else:
                print(f"❌ {description} - 未找到")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 Context结构完整性: {success_rate:.1f}%")
        
        return success_rate > 80
        
    except Exception as e:
        print(f"❌ Context文件检查失败: {str(e)}")
        return False

def test_loading_components():
    """测试加载组件"""
    print("\n⏳ 测试加载组件...")
    
    loading_file = Path("frontend/src/components/LoadingIndicator.js")
    
    if not loading_file.exists():
        print("❌ LoadingIndicator.js 文件不存在")
        return False
    
    try:
        with open(loading_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查加载组件类型
        loading_types = [
            ("ScriptGeneratingLoader", "脚本生成加载器"),
            ("VideoGeneratingLoader", "视频生成加载器"),
            ("FileUploadingLoader", "文件上传加载器"),
            ("ProcessingLoader", "处理加载器"),
            ("SuccessIndicator", "成功指示器"),
            ("ErrorIndicator", "错误指示器"),
            ("FullScreenLoader", "全屏加载器")
        ]
        
        results = []
        
        for loader_type, description in loading_types:
            if loader_type in content:
                print(f"✅ {description}")
                results.append(True)
            else:
                print(f"❌ {description} - 未找到")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 加载组件完整性: {success_rate:.1f}%")
        
        return success_rate > 80
        
    except Exception as e:
        print(f"❌ 加载组件检查失败: {str(e)}")
        return False

def test_step_navigation():
    """测试步骤导航组件"""
    print("\n🧭 测试步骤导航组件...")
    
    nav_file = Path("frontend/src/components/StepNavigation.js")
    
    if not nav_file.exists():
        print("❌ StepNavigation.js 文件不存在")
        return False
    
    try:
        with open(nav_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查导航功能
        features = [
            ("useAppContext", "Context使用"),
            ("isStepAccessible", "步骤访问检查"),
            ("handleStepClick", "步骤点击处理"),
            ("renderProgressInfo", "进度信息渲染"),
            ("renderQuickActions", "快捷操作渲染"),
            ("Steps", "Ant Design Steps组件")
        ]
        
        results = []
        
        for feature, description in features:
            if feature in content:
                print(f"✅ {description}")
                results.append(True)
            else:
                print(f"❌ {description} - 未找到")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 步骤导航功能完整性: {success_rate:.1f}%")
        
        return success_rate > 80
        
    except Exception as e:
        print(f"❌ 步骤导航检查失败: {str(e)}")
        return False

def test_quick_actions():
    """测试快捷操作组件"""
    print("\n⚡ 测试快捷操作组件...")
    
    actions_file = Path("frontend/src/components/QuickActions.js")
    
    if not actions_file.exists():
        print("❌ QuickActions.js 文件不存在")
        return False
    
    try:
        with open(actions_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查操作类型
        action_types = [
            ("baseActions", "基础操作"),
            ("previewActions", "预览操作"),
            ("exportActions", "导出操作"),
            ("editActions", "编辑操作"),
            ("playbackActions", "播放控制操作"),
            ("getActionsForCurrentStep", "步骤相关操作")
        ]
        
        results = []
        
        for action_type, description in action_types:
            if action_type in content:
                print(f"✅ {description}")
                results.append(True)
            else:
                print(f"❌ {description} - 未找到")
                results.append(False)
        
        # 检查渲染模式
        render_modes = ["floating", "inline", "sidebar"]
        for mode in render_modes:
            if f"position === '{mode}'" in content:
                print(f"✅ {mode}模式支持")
            else:
                print(f"❌ {mode}模式 - 未找到")
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 快捷操作功能完整性: {success_rate:.1f}%")
        
        return success_rate > 80
        
    except Exception as e:
        print(f"❌ 快捷操作检查失败: {str(e)}")
        return False

def test_app_integration():
    """测试主应用集成"""
    print("\n🔗 测试主应用集成...")
    
    app_file = Path("frontend/src/App.js")
    
    if not app_file.exists():
        print("❌ App.js 文件不存在")
        return False
    
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查集成组件
        integrations = [
            ("AppProvider", "Context Provider"),
            ("useAppContext", "Context Hook使用"),
            ("StepNavigation", "步骤导航集成"),
            ("FullScreenLoader", "全屏加载器集成"),
            ("Badge", "状态徽章"),
            ("Space", "布局组件")
        ]
        
        results = []
        
        for integration, description in integrations:
            if integration in content:
                print(f"✅ {description}")
                results.append(True)
            else:
                print(f"❌ {description} - 未找到")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 主应用集成完整性: {success_rate:.1f}%")
        
        return success_rate > 80
        
    except Exception as e:
        print(f"❌ 主应用集成检查失败: {str(e)}")
        return False

def generate_optimization_report(results):
    """生成优化报告"""
    print("\n" + "=" * 60)
    print("📊 优化功能测试报告")
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
    
    print("\n🎯 优化建议:")
    if success_rate >= 90:
        print("🎉 优化功能实现优秀！可以继续下一阶段的开发。")
    elif success_rate >= 70:
        print("👍 优化功能基本完成，建议修复失败的测试项。")
    else:
        print("⚠️ 优化功能需要进一步完善，请检查失败的组件。")
    
    print("\n📋 下一步行动:")
    if not results.get("前端组件文件", True):
        print("- 完善缺失的前端组件文件")
    if not results.get("Context结构", True):
        print("- 修复Context状态管理结构")
    if not results.get("加载组件", True):
        print("- 完善加载指示器组件")
    if not results.get("步骤导航", True):
        print("- 修复步骤导航功能")
    if not results.get("快捷操作", True):
        print("- 完善快捷操作面板")
    if not results.get("主应用集成", True):
        print("- 修复主应用组件集成")
    
    return success_rate >= 70

def main():
    """主测试函数"""
    print("🚀 开始优化功能测试")
    print("=" * 60)
    
    # 运行所有测试
    results = {}
    
    results["前端组件文件"] = test_frontend_components()
    results["Context结构"] = test_context_structure()
    results["加载组件"] = test_loading_components()
    results["步骤导航"] = test_step_navigation()
    results["快捷操作"] = test_quick_actions()
    results["主应用集成"] = test_app_integration()
    
    # 生成报告
    success = generate_optimization_report(results)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)