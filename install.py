#!/usr/bin/env python3
"""
AI 短视频制作平台安装脚本
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, cwd=None, shell=False):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command, 
            cwd=cwd, 
            shell=shell, 
            capture_output=True, 
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - 版本符合要求")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - 需要Python 3.8+")
        return False

def check_node():
    """检查Node.js版本"""
    print("检查Node.js版本...")
    success, output = run_command(['node', '--version'])
    if success:
        version = output.strip()
        print(f"✅ Node.js {version} - 已安装")
        return True
    else:
        print("❌ Node.js 未安装")
        print("请从 https://nodejs.org/ 下载安装Node.js 16+")
        return False

def check_ffmpeg():
    """检查FFmpeg"""
    print("检查FFmpeg...")
    success, output = run_command(['ffmpeg', '-version'])
    if success:
        version_line = output.split('\n')[0]
        print(f"✅ {version_line}")
        return True
    else:
        print("❌ FFmpeg 未安装")
        print("请从 https://ffmpeg.org/download.html 下载安装FFmpeg")
        return False

def install_python_deps():
    """安装Python依赖"""
    print("\n安装Python依赖...")
    os.chdir('backend')
    
    # 检查是否有虚拟环境
    if not Path('venv').exists():
        print("创建虚拟环境...")
        success, output = run_command([sys.executable, '-m', 'venv', 'venv'])
        if not success:
            print(f"❌ 创建虚拟环境失败: {output}")
            return False
    
    # 激活虚拟环境并安装依赖
    if platform.system() == "Windows":
        pip_cmd = ['venv\\Scripts\\pip.exe']
    else:
        pip_cmd = ['venv/bin/pip']
    
    print("安装Python包...")
    success, output = run_command(pip_cmd + ['install', '-r', 'requirements.txt'])
    if success:
        print("✅ Python依赖安装成功")
        os.chdir('..')
        return True
    else:
        print(f"❌ Python依赖安装失败: {output}")
        os.chdir('..')
        return False

def install_node_deps():
    """安装Node.js依赖"""
    print("\n安装Node.js依赖...")
    os.chdir('frontend')
    
    # 确定npm命令
    npm_cmd = 'npm.cmd' if platform.system() == "Windows" else 'npm'
    
    print("安装Node.js包...")
    success, output = run_command([npm_cmd, 'install'], shell=True)
    if success:
        print("✅ Node.js依赖安装成功")
        os.chdir('..')
        return True
    else:
        print(f"❌ Node.js依赖安装失败: {output}")
        os.chdir('..')
        return False

def setup_env_file():
    """设置环境变量文件"""
    print("\n设置环境变量...")
    env_example = Path('backend/.env.example')
    env_file = Path('backend/.env')
    
    if env_file.exists():
        print("✅ .env 文件已存在")
        return True
    
    if env_example.exists():
        # 复制示例文件
        with open(env_example, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 已创建 .env 文件")
        print("⚠️  请编辑 backend/.env 文件，填入你的 OpenAI API Key")
        return True
    else:
        print("❌ 找不到 .env.example 文件")
        return False

def create_directories():
    """创建必要的目录"""
    print("\n创建目录结构...")
    dirs = [
        'assets/temp',
        'assets/music', 
        'assets/images',
        'output',
        'templates',
        'uploads/images',
        'uploads/videos',
        'uploads/audio',
        'data/projects',
        'logs'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录结构创建完成")
    return True

def main():
    """主安装函数"""
    print("🚀 AI 短视频制作平台安装程序")
    print("=" * 50)
    
    # 检查系统要求
    checks = [
        ("Python", check_python()),
        ("Node.js", check_node()),
        ("FFmpeg", check_ffmpeg())
    ]
    
    failed_checks = [name for name, result in checks if not result]
    
    if failed_checks:
        print(f"\n❌ 以下依赖检查失败: {', '.join(failed_checks)}")
        print("请安装缺失的依赖后重新运行安装程序")
        return False
    
    print("\n✅ 所有系统依赖检查通过")
    
    # 安装步骤
    steps = [
        ("创建目录", create_directories),
        ("设置环境变量", setup_env_file),
        ("安装Python依赖", install_python_deps),
        ("安装Node.js依赖", install_node_deps)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📦 {step_name}...")
        if not step_func():
            print(f"❌ {step_name}失败")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 安装完成！")
    print("=" * 50)
    print("\n下一步:")
    print("1. 编辑 backend/.env 文件，填入你的 OpenAI API Key")
    print("2. 运行 'python start.py' 启动应用")
    print("3. 访问 http://localhost:3000 使用应用")
    print("\n如有问题，请查看 README.md 文档")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n安装过程中出现错误: {e}")
        sys.exit(1)