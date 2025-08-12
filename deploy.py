#!/usr/bin/env python3
"""
AI 短视频制作平台部署脚本
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, cwd=None):
    """运行命令"""
    print(f"执行: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False

def check_docker():
    """检查 Docker 是否安装"""
    return run_command("docker --version")

def check_docker_compose():
    """检查 Docker Compose 是否安装"""
    return run_command("docker-compose --version")

def build_images():
    """构建 Docker 镜像"""
    print("构建 Docker 镜像...")
    return run_command("docker-compose build")

def start_services():
    """启动服务"""
    print("启动服务...")
    return run_command("docker-compose up -d")

def stop_services():
    """停止服务"""
    print("停止服务...")
    return run_command("docker-compose down")

def check_services():
    """检查服务状态"""
    print("检查服务状态...")
    return run_command("docker-compose ps")

def view_logs():
    """查看日志"""
    print("查看服务日志...")
    return run_command("docker-compose logs -f")

def setup_env():
    """设置环境变量"""
    env_file = Path(".env")
    if not env_file.exists():
        print("创建环境变量文件...")
        env_content = """# AI 短视频制作平台环境变量
OPENAI_API_KEY=your_openai_api_key_here
UNSPLASH_ACCESS_KEY=your_unsplash_key_here

# 数据库配置（如果使用）
# DATABASE_URL=postgresql://user:password@localhost:5432/ai_video_maker

# 其他配置
ENVIRONMENT=production
DEBUG=false
"""
        env_file.write_text(env_content)
        print("✓ 环境变量文件已创建，请编辑 .env 文件配置您的 API 密钥")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="AI 短视频制作平台部署工具")
    parser.add_argument("action", choices=[
        "setup", "build", "start", "stop", "restart", "status", "logs"
    ], help="要执行的操作")
    
    args = parser.parse_args()
    
    print("=== AI 短视频制作平台部署工具 ===\n")
    
    if args.action == "setup":
        print("初始化部署环境...")
        
        # 检查 Docker
        if not check_docker():
            print("✗ Docker 未安装，请先安装 Docker")
            sys.exit(1)
        print("✓ Docker 已安装")
        
        # 检查 Docker Compose
        if not check_docker_compose():
            print("✗ Docker Compose 未安装，请先安装 Docker Compose")
            sys.exit(1)
        print("✓ Docker Compose 已安装")
        
        # 设置环境变量
        if not setup_env():
            print("请配置环境变量后重新运行")
            sys.exit(1)
        
        print("✓ 环境检查完成")
        
    elif args.action == "build":
        if not build_images():
            sys.exit(1)
        print("✓ 镜像构建完成")
        
    elif args.action == "start":
        if not start_services():
            sys.exit(1)
        print("✓ 服务启动完成")
        print("前端地址: http://localhost:3000")
        print("后端 API: http://localhost:8000")
        print("API 文档: http://localhost:8000/docs")
        
    elif args.action == "stop":
        if not stop_services():
            sys.exit(1)
        print("✓ 服务已停止")
        
    elif args.action == "restart":
        print("重启服务...")
        stop_services()
        if not start_services():
            sys.exit(1)
        print("✓ 服务重启完成")
        
    elif args.action == "status":
        check_services()
        
    elif args.action == "logs":
        view_logs()

if __name__ == "__main__":
    main()