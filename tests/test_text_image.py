#!/usr/bin/env python3
"""
测试文字图层生成功能
"""

import os
import sys
from pathlib import Path

# 添加后端路径到Python路径
sys.path.append('backend')

def test_text_image_creation():
    """测试文字图层创建"""
    print("🎨 测试文字图层创建功能...")
    
    try:
        from routers.video_maker import create_text_image, load_font
        from PIL import Image, ImageDraw
        import requests
        
        # 创建测试目录
        test_dir = Path("test_output")
        test_dir.mkdir(exist_ok=True)
        
        # 1. 测试字体加载
        print("测试字体加载...")
        font = load_font(48)
        if font:
            print("✅ 字体加载成功")
        else:
            print("⚠️ 字体加载失败，将使用默认字体")
        
        # 2. 下载测试图片
        print("下载测试图片...")
        test_image_path = test_dir / "test_image.jpg"
        
        if not test_image_path.exists():
            try:
                response = requests.get("https://picsum.photos/1280/720?random=1")
                with open(test_image_path, 'wb') as f:
                    f.write(response.content)
                print("✅ 测试图片下载成功")
            except Exception as e:
                print(f"❌ 下载测试图片失败: {e}")
                # 创建一个简单的测试图片
                img = Image.new('RGB', (1280, 720), color='blue')
                img.save(test_image_path)
                print("✅ 创建了简单的测试图片")
        
        # 3. 测试文字图层创建
        print("测试文字图层创建...")
        test_text = "这是一个测试文字\n用于验证文字图层生成功能"
        output_path = test_dir / "test_text_image.jpg"
        
        success = create_text_image(
            str(test_image_path), 
            test_text, 
            str(output_path)
        )
        
        if success and output_path.exists():
            print("✅ 文字图层创建成功")
            print(f"   输出文件: {output_path}")
            print(f"   文件大小: {output_path.stat().st_size} bytes")
            return True
        else:
            print("❌ 文字图层创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_font_loading():
    """测试不同操作系统的字体加载"""
    print("\n🔤 测试字体加载...")
    
    try:
        import platform
        from routers.video_maker import load_font
        
        print(f"操作系统: {platform.system()}")
        
        # 测试不同字体大小
        sizes = [24, 48, 72]
        for size in sizes:
            font = load_font(size)
            if font:
                print(f"✅ 字体大小 {size} 加载成功")
            else:
                print(f"❌ 字体大小 {size} 加载失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 字体测试失败: {e}")
        return False

def test_pillow_installation():
    """测试Pillow安装和功能"""
    print("\n📦 测试Pillow安装...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("✅ Pillow导入成功")
        
        # 测试基本功能
        img = Image.new('RGB', (100, 100), color='red')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Test", fill='white')
        
        test_path = Path("test_output/pillow_test.jpg")
        test_path.parent.mkdir(exist_ok=True)
        img.save(test_path)
        
        if test_path.exists():
            print("✅ Pillow基本功能正常")
            test_path.unlink()  # 删除测试文件
            return True
        else:
            print("❌ Pillow保存文件失败")
            return False
            
    except Exception as e:
        print(f"❌ Pillow测试失败: {e}")
        return False

def main():
    print("🚀 文字图层生成功能测试")
    print("=" * 40)
    
    # 测试结果
    results = {}
    
    # 1. 测试Pillow安装
    results["Pillow安装"] = test_pillow_installation()
    
    # 2. 测试字体加载
    results["字体加载"] = test_font_loading()
    
    # 3. 测试文字图层创建
    results["文字图层创建"] = test_text_image_creation()
    
    # 输出结果
    print("\n" + "=" * 40)
    print("📋 测试结果汇总")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:12} : {status}")
        if result:
            passed += 1
    
    print("-" * 40)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！文字图层功能正常")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        print("\n🔧 可能的解决方案:")
        print("1. 确保Pillow正确安装: pip install Pillow")
        print("2. 检查系统字体是否可用")
        print("3. 确保有足够的磁盘空间")
        print("4. 检查文件权限")
    
    print("\n测试完成！")
    return passed == total

if __name__ == "__main__":
    main()