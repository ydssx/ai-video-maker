"""
生活方式模板
"""

def get_food_style():
    """美食风格"""
    return {
        "name": "美食诱惑",
        "description": "温暖的美食风格，适合美食分享和餐厅推广",
        "font_size": 46,
        "font_color": (255, 255, 255),
        "font_shadow": (139, 69, 19),  # 棕色阴影
        "text_position": "bottom",
        "background_overlay": (139, 69, 19, 100),  # 棕色遮罩
        "transition": "fade",
        "text_animation": "slide_up",
        "color_scheme": ["#dc2626", "#ea580c", "#ca8a04"]
    }

def get_travel_style():
    """旅游风格"""
    return {
        "name": "旅行探索",
        "description": "清新的旅游风格，适合旅游攻略和风景分享",
        "font_size": 44,
        "font_color": (255, 255, 255),
        "font_shadow": (0, 100, 200),  # 蓝色阴影
        "text_position": "center",
        "background_overlay": (0, 100, 200, 80),  # 蓝色遮罩
        "transition": "zoom",
        "text_animation": "fade_in",
        "color_scheme": ["#0ea5e9", "#06b6d4", "#10b981"]
    }

def get_fitness_style():
    """健身运动风格"""
    return {
        "name": "健身运动",
        "description": "动感的运动风格，适合健身和运动内容",
        "font_size": 50,
        "font_color": (255, 255, 255),
        "font_shadow": (0, 0, 0),
        "text_position": "center",
        "background_overlay": (34, 197, 94, 120),  # 绿色遮罩
        "transition": "slide",
        "text_animation": "bounce_in",
        "color_scheme": ["#22c55e", "#16a34a", "#15803d"]
    }

def get_beauty_style():
    """美妆时尚风格"""
    return {
        "name": "美妆时尚",
        "description": "时尚的美妆风格，适合美妆教程和时尚分享",
        "font_size": 42,
        "font_color": (255, 255, 255),
        "font_shadow": (219, 39, 119),  # 粉色阴影
        "text_position": "top",
        "background_overlay": (219, 39, 119, 100),  # 粉色遮罩
        "transition": "fade",
        "text_animation": "slide_down",
        "color_scheme": ["#db2777", "#e879f9", "#f472b6"]
    }