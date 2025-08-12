#!/usr/bin/env python3
"""
测试前端构建
"""

import subprocess
import os
import sys
from pathlib import Path

def test_frontend_build():
    """测试前端构建"""
    print("测试前端构建...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ 前端目录不存在")
        return False
    
    os.chdir(frontend_dir)
    
    try:
        # 检查依赖是否安装
        if not Path("node_modules").exists():
            print("安装前端依赖...")
            result = subprocess.run(["npm", "install"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ 依赖安装失败: {result.stderr}")
                return False
            print("✅ 依赖安装成功")
        
        # 尝试构建
        print("开始构建...")
        result = subprocess.run(["npm", "run", "build"], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ 前端构建成功")
            return True
        else:
            print(f"❌ 前端构建失败:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 构建超时")
        return False
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False
    finally:
        os.chdir("..")

def test_backend_import():
    """测试后端导入"""
    print("\n测试后端模块导入...")
    
    try:
        # 添加后端目录到 Python 路径
        sys.path.insert(0, "backend")
        
        # 测试主要模块导入
        import main
        print("✅ main.py 导入成功")
        
        import models
        print("✅ models.py 导入成功")
        
        from routers import script_generator, video_maker, assets, stats
        print("✅ 所有路由模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 后端导入失败: {e}")
        return False

def main():
    print("=== 应用构建测试 ===\n")
    
    # 测试后端导入
    backend_ok = test_backend_import()
    
    # 测试前端构建
    frontend_ok = test_frontend_build()
    
    print(f"\n=== 测试结果 ===")
    print(f"后端模块: {'✅ 通过' if backend_ok else '❌ 失败'}")
    print(f"前端构建: {'✅ 通过' if frontend_ok else '❌ 失败'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 所有测试通过！应用可以正常构建和运行。")
        return True
    else:
        print("\n⚠ 部分测试失败，请检查错误信息。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)