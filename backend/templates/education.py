"""
教育培训模板
"""

def get_academic_style():
    """学术教育风格"""
    return {
        "name": "学术教育",
        "description": "严谨的学术风格，适合教育机构和学术内容",
        "font_size": 44,
        "font_color": (255, 255, 255),
        "font_shadow": (30, 58, 138),  # 深蓝阴影
        "text_position": "center",
        "background_overlay": (30, 58, 138, 120),  # 深蓝遮罩
        "transition": "fade",
        "text_animation": "fade_in",
        "color_scheme": ["#1e3a8a", "#3730a3", "#4338ca"]
    }

def get_kids_style():
    """儿童教育风格"""
    return {
        "name": "儿童教育",
        "description": "活泼可爱的儿童风格，适合儿童教育内容",
        "font_size": 48,
        "font_color": (255, 255, 255),
        "font_shadow": (251, 191, 36),  # 黄色阴影
        "text_position": "center",
        "background_overlay": (251, 191, 36, 100),  # 黄色遮罩
        "transition": "bounce",
        "text_animation": "bounce_in",
        "color_scheme": ["#fbbf24", "#f59e0b", "#d97706"]
    }

def get_language_style():
    """语言学习风格"""
    return {
        "name": "语言学习",
        "description": "国际化的语言学习风格，适合语言教学",
        "font_size": 46,
        "font_color": (255, 255, 255),
        "font_shadow": (16, 185, 129),  # 绿色阴影
        "text_position": "bottom",
        "background_overlay": (16, 185, 129, 100),  # 绿色遮罩
        "transition": "slide",
        "text_animation": "slide_in",
        "color_scheme": ["#10b981", "#059669", "#047857"]
    }

def get_skill_style():
    """技能培训风格"""
    return {
        "name": "技能培训",
        "description": "专业的技能培训风格，适合职业技能教学",
        "font_size": 44,
        "font_color": (255, 255, 255),
        "font_shadow": (120, 53, 15),  # 橙色阴影
        "text_position": "center",
        "background_overlay": (120, 53, 15, 120),  # 橙色遮罩
        "transition": "fade",
        "text_animation": "fade_in",
        "color_scheme": ["#ea580c", "#dc2626", "#b91c1c"]
    }