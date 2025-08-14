#!/usr/bin/env python3
"""
MySQL数据库设置脚本
帮助用户快速配置MySQL数据库
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

def check_mysql_installed():
    """检查MySQL是否已安装"""
    try:
        result = subprocess.run(['mysql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] MySQL客户端已安装")
            return True
        else:
            print("[ERROR] MySQL客户端未安装")
            return False
    except FileNotFoundError:
        print("[ERROR] MySQL客户端未安装")
        return False

def test_mysql_connection(host, port, user, password):
    """测试MySQL连接"""
    try:
        import pymysql
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password
        )
        connection.close()
        return True
    except Exception as e:
        print(f"连接失败: {str(e)}")
        return False

def create_database(host, port, user, password, database):
    """创建数据库"""
    try:
        import pymysql
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"[OK] 数据库 '{database}' 创建成功")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"创建数据库失败: {str(e)}")
        return False

def update_env_file(host, port, user, password, database):
    """更新.env文件"""
    env_path = Path("backend/.env")
    
    # 构建MySQL URL
    mysql_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    
    # 读取现有.env文件或创建新的
    env_content = ""
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # 更新或添加数据库配置
    lines = env_content.split('\n')
    updated_lines = []
    database_url_updated = False
    
    for line in lines:
        if line.startswith('DATABASE_URL='):
            updated_lines.append(f'DATABASE_URL={mysql_url}')
            database_url_updated = True
        elif line.startswith('MYSQL_HOST='):
            updated_lines.append(f'MYSQL_HOST={host}')
        elif line.startswith('MYSQL_PORT='):
            updated_lines.append(f'MYSQL_PORT={port}')
        elif line.startswith('MYSQL_USER='):
            updated_lines.append(f'MYSQL_USER={user}')
        elif line.startswith('MYSQL_PASSWORD='):
            updated_lines.append(f'MYSQL_PASSWORD={password}')
        elif line.startswith('MYSQL_DATABASE='):
            updated_lines.append(f'MYSQL_DATABASE={database}')
        else:
            updated_lines.append(line)
    
    # 如果没有找到DATABASE_URL，添加它
    if not database_url_updated:
        updated_lines.extend([
            '',
            '# 数据库配置',
            f'DATABASE_URL={mysql_url}',
            f'MYSQL_HOST={host}',
            f'MYSQL_PORT={port}',
            f'MYSQL_USER={user}',
            f'MYSQL_PASSWORD={password}',
            f'MYSQL_DATABASE={database}',
            'MYSQL_CHARSET=utf8mb4'
        ])
    
    # 写入文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"[OK] 配置已保存到 {env_path}")

def install_dependencies():
    """安装Python依赖"""
    print("安装Python依赖...")
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'sqlalchemy==2.0.23', 'pymysql==1.1.0', 'alembic==1.13.1'
        ], check=True)
        print("[OK] Python依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Python依赖安装失败: {str(e)}")
        return False

def main():
    print("=== AI视频制作平台 MySQL 数据库设置 ===\n")
    
    # 检查MySQL
    # if not check_mysql_installed():
    #     print("\n请先安装MySQL:")
    #     print("- Windows: https://dev.mysql.com/downloads/mysql/")
    #     print("- macOS: brew install mysql")
    #     print("- Ubuntu: sudo apt install mysql-server")
    #     return 1
    
    # 安装Python依赖
    if not install_dependencies():
        return 1
    
    print("\n请输入MySQL连接信息:")
    
    # 获取连接信息
    host = input("MySQL主机地址 [localhost]: ").strip() or "localhost"
    port = input("MySQL端口 [3306]: ").strip() or "3306"
    user = input("MySQL用户名 [root]: ").strip() or "root"
    password = getpass.getpass("MySQL密码: ")
    database = input("数据库名称 [ai_video_maker]: ").strip() or "ai_video_maker"
    
    print(f"\n连接信息:")
    print(f"主机: {host}")
    print(f"端口: {port}")
    print(f"用户: {user}")
    print(f"数据库: {database}")
    
    # 测试连接
    print("\n测试MySQL连接...")
    if not test_mysql_connection(host, port, user, password):
        print("请检查MySQL连接信息")
        return 1
    
    print("[OK] MySQL连接成功")
    
    # 创建数据库
    print(f"\n创建数据库 '{database}'...")
    if not create_database(host, port, user, password, database):
        return 1
    
    # 更新配置文件
    print("\n更新配置文件...")
    update_env_file(host, port, user, password, database)
    
    # 测试数据库服务
    print("\n测试数据库服务...")
    try:
        # 首先测试模型定义
        result = subprocess.run([
            sys.executable, 'test_mysql_connection.py', '--test-models-only'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("[ERROR] 数据库模型测试失败")
            print(result.stderr)
            return 1
        
        # 然后测试实际连接
        mysql_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        result = subprocess.run([
            sys.executable, 'test_mysql_connection.py', '--mysql-url', mysql_url
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] 数据库服务测试成功")
        else:
            print("[ERROR] 数据库服务测试失败")
            print(result.stderr)
            return 1
            
    except Exception as e:
        print(f"[ERROR] 数据库服务测试失败: {str(e)}")
        return 1
    
    print("\n[SUCCESS] MySQL数据库设置完成！")
    print("\n接下来你可以:")
    print("1. 运行 'python start.py' 启动应用")
    print("2. 如果需要从SQLite迁移数据，运行:")
    print(f"   python backend/migrate_to_mysql.py --mysql-url '{mysql_url}'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())