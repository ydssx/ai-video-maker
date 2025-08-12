#!/usr/bin/env python3
"""
视频下载问题调试工具
"""

import os
import requests
import json
from pathlib import Path

def check_output_directory():
    """检查输出目录"""
    output_dir = Path("output")
    print(f"检查输出目录: {output_dir.absolute()}")
    
    if not output_dir.exists():
        print("❌ 输出目录不存在")
        return False
    
    print("✅ 输出目录存在")
    
    # 列出所有视频文件
    video_files = list(output_dir.glob("*.mp4"))
    print(f"找到 {len(video_files)} 个视频文件:")
    
    for video_file in video_files:
        size = video_file.stat().st_size
        print(f"  - {video_file.name} ({size} bytes)")
    
    return len(video_files) > 0

def test_static_file_access():
    """测试静态文件访问"""
    print("\n测试静态文件访问...")
    
    try:
        # 测试输出目录访问
        response = requests.get("http://localhost:8000/output/", timeout=5)
        print(f"输出目录访问状态: {response.status_code}")
        
        # 如果有视频文件，测试访问
        output_dir = Path("output")
        video_files = list(output_dir.glob("*.mp4"))
        
        if video_files:
            test_file = video_files[0]
            test_url = f"http://localhost:8000/output/{test_file.name}"
            print(f"测试视频文件访问: {test_url}")
            
            response = requests.head(test_url, timeout=10)
            print(f"视频文件访问状态: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 视频文件可以正常访问")
                print(f"Content-Type: {response.headers.get('content-type')}")
                print(f"Content-Length: {response.headers.get('content-length')}")
            else:
                print("❌ 视频文件无法访问")
        else:
            print("⚠ 没有视频文件可供测试")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True

def test_download_api():
    """测试下载 API"""
    print("\n测试下载 API...")
    
    try:
        # 获取视频状态
        response = requests.get("http://localhost:8000/api/video/status/test", timeout=5)
        print(f"视频状态 API 测试: {response.status_code}")
        
        if response.status_code == 404:
            print("⚠ 没有测试视频，这是正常的")
        
        # 测试下载端点
        response = requests.get("http://localhost:8000/api/video/download/test", timeout=5)
        print(f"下载 API 测试: {response.status_code}")
        
        if response.status_code == 404:
            print("⚠ 没有测试视频可下载，这是正常的")
        
    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        return False
    
    return True

def check_permissions():
    """检查文件权限"""
    print("\n检查文件权限...")
    
    output_dir = Path("output")
    if not output_dir.exists():
        print("❌ 输出目录不存在")
        return False
    
    # 检查目录权限
    if os.access(output_dir, os.R_OK):
        print("✅ 输出目录可读")
    else:
        print("❌ 输出目录不可读")
        return False
    
    # 检查视频文件权限
    video_files = list(output_dir.glob("*.mp4"))
    for video_file in video_files:
        if os.access(video_file, os.R_OK):
            print(f"✅ {video_file.name} 可读")
        else:
            print(f"❌ {video_file.name} 不可读")
            return False
    
    return True

def generate_test_video():
    """生成测试视频"""
    print("\n生成测试视频...")
    
    try:
        # 创建一个简单的测试视频
        from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
        
        # 创建背景
        background = ColorClip(size=(1280, 720), color=(0, 100, 200), duration=3)
        
        # 创建文字
        text = TextClip("测试视频", fontsize=50, color='white', font='Arial')
        text = text.set_position('center').set_duration(3)
        
        # 合成视频
        video = CompositeVideoClip([background, text])
        
        # 导出
        output_path = "output/test_video.mp4"
        os.makedirs("output", exist_ok=True)
        
        video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            verbose=False,
            logger=None
        )
        
        print(f"✅ 测试视频已生成: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 生成测试视频失败: {e}")
        return False

def main():
    print("=== 视频下载问题调试工具 ===\n")
    
    # 检查输出目录
    has_videos = check_output_directory()
    
    # 如果没有视频，生成一个测试视频
    if not has_videos:
        print("\n没有找到视频文件，尝试生成测试视频...")
        generate_test_video()
        has_videos = check_output_directory()
    
    # 检查权限
    check_permissions()
    
    # 测试静态文件访问
    test_static_file_access()
    
    # 测试下载 API
    test_download_api()
    
    print("\n=== 调试完成 ===")
    print("如果仍有问题，请检查:")
    print("1. 后端服务是否正常运行")
    print("2. 视频文件是否真的存在")
    print("3. 文件权限是否正确")
    print("4. 浏览器控制台是否有错误信息")

if __name__ == "__main__":
    main()