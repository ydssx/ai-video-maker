#!/usr/bin/env python3
"""
Windows 专用启动脚本
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_node():
    """检查 Node.js 是否安装"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✓ Node.js 版本: {result.stdout.strip()}")
            return True
    except:
        pass
    
    print("✗ Node.js 未安装或不在 PATH 中")
    return False

def check_npm():
    """检查 npm 是否安装"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✓ npm 版本: {result.stdout.strip()}")
            return True
    except:
        pass
    
    print("✗ npm 未安装或不在 PATH 中")
    return False

def install_frontend_deps():
    """安装前端依赖"""
    print("检查前端依赖...")
    
    if not Path('frontend/node_modules').exists():
        print("安装前端依赖...")
        os.chdir('frontend')
        
        try:
            # 使用 shell=True 在 Windows 上执行
            result = subprocess.run(['npm', 'install'], shell=True, check=True)
            print("✓ 前端依赖安装完成")
        except subprocess.CalledProcessError as e:
            print(f"✗ 前端依赖安装失败: {e}")
            return False
        finally:
            os.chdir('..')
    else:
        print("✓ 前端依赖已安装")
    
    return True

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    
    try:
        # 启动后端服务
        backend_process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 
            'main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000',
            '--reload'
        ], cwd='backend')
        
        print("✓ 后端服务启动成功 (http://localhost:8000)")
        return backend_process
    except Exception as e:
        print(f"✗ 后端服务启动失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("启动前端服务...")
    
    try:
        # 启动前端服务
        frontend_process = subprocess.Popen([
            'npm', 'start'
        ], cwd='frontend', shell=True)
        
        print("✓ 前端服务启动成功 (http://localhost:3000)")
        return frontend_process
    except Exception as e:
        print(f"✗ 前端服务启动失败: {e}")
        return None

def main():
    print("=== AI 短视频制作平台 Windows 启动器 ===\n")
    
    # 检查环境
    if not check_node():
        print("请安装 Node.js: https://nodejs.org/")
        sys.exit(1)
    
    if not check_npm():
        print("请确保 npm 已正确安装")
        sys.exit(1)
    
    # 检查环境变量文件
    if not Path('backend/.env').exists():
        print("创建环境变量文件...")
        env_content = """OPENAI_API_KEY=your_openai_api_key_here
UNSPLASH_ACCESS_KEY=your_unsplash_key_here"""
        Path('backend/.env').write_text(env_content)
        print("✓ 环境变量文件已创建")
    
    # 安装前端依赖
    if not install_frontend_deps():
        sys.exit(1)
    
    # 启动服务
    print("\n启动服务...")
    
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # 等待后端启动
    time.sleep(3)
    
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 所有服务启动成功！")
    print("前端地址: http://localhost:3000")
    print("后端 API: http://localhost:8000")
    print("API 文档: http://localhost:8000/docs")
    print("\n按 Ctrl+C 停止服务")
    
    try:
        # 等待用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        if frontend_process:
            frontend_process.terminate()
        if backend_process:
            backend_process.terminate()
        print("服务已停止")

if __name__ == "__main__":
    main()