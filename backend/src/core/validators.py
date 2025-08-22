"""
验证工具

包含各种验证函数，用于验证输入数据。
"""
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, ValidationError, validator


def validate_password(password: str) -> str:
    """
    验证密码复杂度
    
    Args:
        password: 要验证的密码
        
    Returns:
        str: 验证通过的密码
        
    Raises:
        ValueError: 如果密码不符合复杂度要求
    """
    if len(password) < 8:
        raise ValueError("密码长度不能少于8个字符")
    
    if not any(char.isdigit() for char in password):
        raise ValueError("密码必须包含至少一个数字")
    
    if not any(char.isalpha() for char in password):
        raise ValueError("密码必须包含至少一个字母")
    
    # 检查是否包含特殊字符
    # special_chars = r'[!@#$%^&*(),.?":{}|<>]'
    # if not re.search(special_chars, password):
    #     raise ValueError("密码必须包含至少一个特殊字符")
    
    return password


def validate_email(email: str) -> str:
    """
    验证电子邮箱格式
    
    Args:
        email: 要验证的电子邮箱
        
    Returns:
        str: 验证通过的电子邮箱
        
    Raises:
        ValueError: 如果电子邮箱格式不正确
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValueError("无效的电子邮箱格式")
    return email


def validate_username(username: str) -> str:
    """
    验证用户名格式
    
    Args:
        username: 要验证的用户名
        
    Returns:
        str: 验证通过的用户名
        
    Raises:
        ValueError: 如果用户名格式不正确
    """
    if len(username) < 3:
        raise ValueError("用户名长度不能少于3个字符")
    
    if len(username) > 50:
        raise ValueError("用户名长度不能超过50个字符")
    
    # 只允许字母、数字、下划线和连字符
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValueError("用户名只能包含字母、数字、下划线和连字符")
    
    return username


def validate_dict_keys(
    data: Dict[str, Any], 
    required_keys: List[str], 
    optional_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    验证字典中是否包含必需的键
    
    Args:
        data: 要验证的字典
        required_keys: 必需的键列表
        optional_keys: 可选的键列表
        
    Returns:
        Dict[str, Any]: 验证通过的字典
        
    Raises:
        ValueError: 如果缺少必需的键或包含无效的键
    """
    optional_keys = optional_keys or []
    all_keys = set(required_keys) | set(optional_keys)
    
    # 检查是否缺少必需的键
    missing_keys = set(required_keys) - set(data.keys())
    if missing_keys:
        raise ValueError(f"缺少必需的键: {', '.join(missing_keys)}")
    
    # 检查是否包含无效的键
    invalid_keys = set(data.keys()) - all_keys
    if invalid_keys:
        raise ValueError(f"包含无效的键: {', '.join(invalid_keys)}")
    
    return data


def validate_pagination_params(
    skip: int = 0, 
    limit: int = 100, 
    max_limit: int = 1000
) -> Tuple[int, int]:
    """
    验证分页参数
    
    Args:
        skip: 跳过的记录数
        limit: 每页记录数
        max_limit: 每页最大记录数
        
    Returns:
        Tuple[int, int]: 验证后的(skip, limit)
        
    Raises:
        ValueError: 如果参数无效
    """
    if skip < 0:
        raise ValueError("skip不能为负数")
    
    if limit <= 0:
        raise ValueError("limit必须大于0")
    
    if limit > max_limit:
        raise ValueError(f"每页记录数不能超过{max_limit}")
    
    return skip, limit


def validate_model(
    model: BaseModel, 
    data: Union[Dict[str, Any], BaseModel],
    exclude_unset: bool = False
) -> BaseModel:
    """
    使用Pydantic模型验证数据
    
    Args:
        model: Pydantic模型类
        data: 要验证的数据
        exclude_unset: 是否排除未设置的字段
        
    Returns:
        BaseModel: 验证后的模型实例
        
    Raises:
        ValidationError: 如果验证失败
    """
    if isinstance(data, dict):
        return model(**(data if not exclude_unset else {
            k: v for k, v in data.items() if v is not None
        }))
    return model.parse_obj(data)
