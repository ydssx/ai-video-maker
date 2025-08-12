"""
商务风格模板
"""

def get_corporate_style():
    """企业商务风格"""
    return {
        "name": "企业商务",
        "description": "专业商务风格，适合企业宣传和产品介绍",
        "font_size": 44,
        "font_color": (255, 255, 255),
        "font_shadow": (0, 0, 0),
        "text_position": "bottom",
        "background_overlay": (0, 0, 0, 150),  # 深色遮罩
        "transition": "slide",
        "text_animation": "fade_in",
        "logo_position": "top_right",
        "color_scheme": ["#1e3a8a", "#3b82f6", "#60a5fa"]
    }

def get_startup_style():
    """创业公司风格"""
    return {
        "name": "创业活力",
        "description": "年轻活力的创业风格，适合新兴企业",
        "font_size": 46,
        "font_color": (255, 255, 255),
        "font_shadow": (0, 0, 0),
        "text_position": "center",
        "background_overlay": (255, 107, 107, 120),  # 红色遮罩
        "transition": "zoom",
        "text_animation": "bounce_in",
        "color_scheme": ["#ef4444", "#f97316", "#eab308"]
    }

def get_finance_style():
    """金融理财风格"""
    return {
        "name": "金融理财",
        "description": "稳重专业的金融风格，适合理财和投资内容",
        "font_size": 42,
        "font_color": (255, 215, 0),  # 金色
        "font_shadow": (0, 0, 0),
        "text_position": "center",
        "background_overlay": (0, 0, 0, 180),  # 深色遮罩
        "transition": "fade",
        "text_animation": "slide_up",
        "color_scheme": ["#1f2937", "#374151", "#ffd700"]
    }

def get_ecommerce_style():
    """电商购物风格"""
    return {
        "name": "电商购物",
        "description": "活泼的购物风格，适合产品展示和促销",
        "font_size": 48,
        "font_color": (255, 255, 255),
        "font_shadow": (255, 20, 147),  # 粉色阴影
        "text_position": "bottom",
        "background_overlay": (255, 20, 147, 100),  # 粉色遮罩
        "transition": "slide",
        "text_animation": "pulse",
        "color_scheme": ["#ec4899", "#f472b6", "#fbbf24"]
    }