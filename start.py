#!/usr/bin/env python3
"""
AI 短视频制作平台启动脚本
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("检查依赖...")
    
    # 检查 Python 依赖
    try:
        import fastapi
        import uvicorn
        import moviepy
        import openai
        print("✓ Python 依赖已安装")
    except ImportError as e:
        print(f"✗ 缺少 Python 依赖: {e}")
        print("请运行: pip install -r backend/requirements.txt")
        return False
    
    # 检查 FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✓ FFmpeg 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg 未安装")
        print("请安装 FFmpeg: https://ffmpeg.org/download.html")
        return False
    
    return True

def setup_directories():
    """创建必要的目录"""
    dirs = [
        'assets/temp',
        'assets/music', 
        'assets/images',
        'output',
        'templates'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✓ 目录结构创建完成")

def check_env_file():
    """检查环境变量文件"""
    env_file = Path('backend/.env')
    if not env_file.exists():
        print("⚠ 未找到 .env 文件")
        print("请复制 backend/.env.example 到 backend/.env 并配置 API 密钥")
        return False
    
    print("✓ 环境变量文件存在")
    return True

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    os.chdir('backend')
    
    try:
        subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 
            'main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000',
            '--reload'
        ])
        print("✓ 后端服务启动成功 (http://localhost:8000)")
    except Exception as e:
        print(f"✗ 后端服务启动失败: {e}")
        return False
    
    os.chdir('..')
    return True

def get_npm_command():
    """获取正确的 npm 命令"""
    import platform
    if platform.system() == "Windows":
        return "npm.cmd"
    return "npm"

def start_frontend():
    """启动前端服务"""
    print("启动前端服务...")
    os.chdir('frontend')
    
    npm_cmd = get_npm_command()
    
    # 检查是否安装了 npm 依赖
    if not Path('node_modules').exists():
        print("安装前端依赖...")
        try:
            subprocess.run([npm_cmd, 'install'], check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"✗ 前端依赖安装失败: {e}")
            return False
    
    try:
        # 在 Windows 上使用 shell=True
        subprocess.Popen([npm_cmd, 'start'], shell=True)
        print("✓ 前端服务启动成功 (http://localhost:3000)")
    except Exception as e:
        print(f"✗ 前端服务启动失败: {e}")
        return False
    
    os.chdir('..')
    return True

def main():
    print("=== AI 短视频制作平台启动器 ===\n")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 设置目录
    setup_directories()
    
    # 检查环境变量
    if not check_env_file():
        print("\n请配置环境变量后重新运行")
        sys.exit(1)
    
    # 启动服务
    print("\n启动服务...")
    
    if start_backend():
        time.sleep(2)  # 等待后端启动
        if start_frontend():
            print("\n🎉 所有服务启动成功！")
            print("前端地址: http://localhost:3000")
            print("后端 API: http://localhost:8000")
            print("API 文档: http://localhost:8000/docs")
            print("\n按 Ctrl+C 停止服务")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n服务已停止")
        else:
            print("前端启动失败")
    else:
        print("后端启动失败")

if __name__ == "__main__":
    main()