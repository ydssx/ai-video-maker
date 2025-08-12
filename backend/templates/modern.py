"""
现代风格模板
"""

def get_modern_style():
    return {
        "name": "现代简约",
        "description": "简洁现代的设计风格，适合商务和科技内容",
        "font_size": 42,
        "font_color": (45, 45, 45),  # 深灰色
        "font_shadow": (200, 200, 200),  # 浅灰阴影
        "text_position": "bottom",
        "background_overlay": (255, 255, 255, 100),  # 半透明白色遮罩
        "transition": "slide",
        "text_animation": "fade_in"
    }

def get_tech_style():
    return {
        "name": "科技风格",
        "description": "科技感十足，适合技术和创新内容",
        "font_size": 46,
        "font_color": (0, 255, 255),  # 青色
        "font_shadow": (0, 0, 0),  # 黑色阴影
        "text_position": "center",
        "background_overlay": (0, 0, 0, 120),  # 半透明黑色遮罩
        "transition": "zoom",
        "text_animation": "typewriter"
    }

def get_elegant_style():
    return {
        "name": "优雅风格",
        "description": "优雅精致，适合生活方式和艺术内容",
        "font_size": 40,
        "font_color": (139, 69, 19),  # 棕色
        "font_shadow": (255, 248, 220),  # 米色阴影
        "text_position": "top",
        "background_overlay": (255, 248, 220, 80),  # 半透明米色遮罩
        "transition": "fade",
        "text_animation": "slide_up"
    }