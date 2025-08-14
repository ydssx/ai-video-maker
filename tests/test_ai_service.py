#!/usr/bin/env python3
"""
AI服务功能测试脚本
"""

import sys
import os
import asyncio
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ai_service import AIService

async def test_script_generation():
    """测试脚本生成功能"""
    print("🎬 测试脚本生成功能...")
    
    ai_service = AIService()
    
    test_cases = [
        {"topic": "人工智能", "style": "教育", "duration": "1分钟"},
        {"topic": "健康饮食", "style": "营销", "duration": "90秒"},
        {"topic": "旅游攻略", "style": "娱乐", "duration": "2分钟"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {case['topic']} - {case['style']}风格")
        
        try:
            script = await ai_service.generate_script(
                topic=case["topic"],
                style=case["style"],
                duration=case["duration"]
            )
            
            print(f"✅ 脚本生成成功")
            print(f"   标题: {script.get('title', 'N/A')}")
            print(f"   场景数量: {len(script.get('scenes', []))}")
            
            # 显示第一个场景的详细信息
            if script.get('scenes'):
                first_scene = script['scenes'][0]
                print(f"   第一场景: {first_scene.get('text', 'N/A')}")
                print(f"   旁白: {first_scene.get('voiceover', 'N/A')[:50]}...")
            
        except Exception as e:
            print(f"❌ 脚本生成失败: {str(e)}")

async def test_voice_generation():
    """测试语音生成功能"""
    print("\n🎵 测试语音生成功能...")
    
    ai_service = AIService()
    
    test_text = "这是一个语音生成测试，用来验证TTS功能是否正常工作。"
    
    # 测试不同的语音配置
    voice_configs = [
        {"provider": "gtts", "voice": "zh", "speed": 1.0},
        {"provider": "gtts", "voice": "zh", "speed": 1.2},
        {"provider": "gtts", "voice": "en", "speed": 0.8},
    ]
    
    for i, config in enumerate(voice_configs, 1):
        print(f"\n🔊 测试配置 {i}: {config}")
        
        try:
            audio_path = await ai_service.generate_voice(test_text, config)
            
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"✅ 语音生成成功")
                print(f"   文件路径: {audio_path}")
                print(f"   文件大小: {file_size} bytes")
                
                # 清理临时文件
                os.unlink(audio_path)
            else:
                print(f"❌ 语音文件未生成")
                
        except Exception as e:
            print(f"❌ 语音生成失败: {str(e)}")

async def test_content_optimization():
    """测试内容优化功能"""
    print("\n✨ 测试内容优化功能...")
    
    ai_service = AIService()
    
    test_content = "这个产品很好用，大家可以试试看。"
    
    try:
        optimized = await ai_service.optimize_content(test_content)
        
        print(f"📝 原始内容: {test_content}")
        print(f"✨ 优化后: {optimized}")
        
        if optimized != test_content:
            print("✅ 内容优化成功")
        else:
            print("ℹ️ 内容未改变（可能是API未配置）")
            
    except Exception as e:
        print(f"❌ 内容优化失败: {str(e)}")

def test_helper_functions():
    """测试辅助函数"""
    print("\n🔧 测试辅助函数...")
    
    ai_service = AIService()
    
    # 测试时长解析
    duration_tests = ["1分钟", "90秒", "2.5分钟", "120秒"]
    
    print("⏱️ 时长解析测试:")
    for duration in duration_tests:
        parsed = ai_service._parse_duration(duration)
        print(f"   {duration} -> {parsed} 分钟")
    
    # 测试提示词构建
    print("\n📝 提示词构建测试:")
    prompt = ai_service._build_script_prompt("人工智能", "教育", "1分钟", 4)
    print(f"   提示词长度: {len(prompt)} 字符")
    print(f"   包含关键词: {'人工智能' in prompt and '教育' in prompt}")

async def main():
    """主测试函数"""
    print("🚀 开始AI服务功能测试\n")
    print("=" * 50)
    
    # 检查环境
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "your_openai_api_key_here":
        print("✅ OpenAI API密钥已配置")
    else:
        print("⚠️ OpenAI API密钥未配置，将使用模板生成")
    
    print("=" * 50)
    
    # 运行测试
    await test_script_generation()
    await test_voice_generation()
    await test_content_optimization()
    test_helper_functions()
    
    print("\n" + "=" * 50)
    print("🎉 AI服务功能测试完成")

if __name__ == "__main__":
    asyncio.run(main())