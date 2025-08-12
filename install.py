#!/usr/bin/env python3
"""
AI 短视频制作平台安装脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def install_python_deps():
    """安装 Python 依赖"""
    print("安装 Python 依赖...")
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            '-r', 'backend/requirements.txt'
        ], check=True)
        print("✓ Python 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("✗ Python 依赖安装失败")
        return False

def get_npm_command():
    """获取正确的 npm 命令"""
    import platform
    if platform.system() == "Windows":
        return "npm.cmd"
    return "npm"

def install_node_deps():
    """安装 Node.js 依赖"""
    print("安装前端依赖...")
    os.chdir('frontend')
    
    npm_cmd = get_npm_command()
    
    try:
        subprocess.run([npm_cmd, 'install'], check=True, shell=True)
        print("✓ 前端依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 前端依赖安装失败: {e}")
        return False
    finally:
        os.chdir('..')

def setup_env_file():
    """设置环境变量文件"""
    env_example = Path('backend/.env.example')
    env_file = Path('backend/.env')
    
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✓ 环境变量文件已创建")
        print("请编辑 backend/.env 文件，配置您的 API 密钥")
    else:
        print("✓ 环境变量文件已存在")

def create_directories():
    """创建必要目录"""
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

def main():
    print("=== AI 短视频制作平台安装器 ===\n")
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print("✗ 需要 Python 3.8 或更高版本")
        sys.exit(1)
    
    print(f"✓ Python 版本: {sys.version}")
    
    # 安装依赖
    if not install_python_deps():
        sys.exit(1)
    
    if not install_node_deps():
        sys.exit(1)
    
    # 设置配置
    setup_env_file()
    create_directories()
    
    print("\n🎉 安装完成！")
    print("\n下一步:")
    print("1. 编辑 backend/.env 文件，配置 OpenAI API 密钥")
    print("2. 运行 python start.py 启动服务")
    print("3. 访问 http://localhost:3000 使用应用")

if __name__ == "__main__":
    main()