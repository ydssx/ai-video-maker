"""
基础模型

包含所有Pydantic模型的基类。
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic.generics import GenericModel

# 定义泛型类型变量
T = TypeVar('T')


class BaseModel(PydanticBaseModel):
    """
    基础模型
    
    所有请求/响应模型的基类
    """
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        orm_mode = True
        allow_population_by_field_name = True


class BaseResponse(BaseModel, GenericModel, Generic[T]):
    """
    基础响应模型
    
    所有API响应的基类
    """
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    
    @classmethod
    def success_response(
        cls, 
        data: Optional[T] = None, 
        message: Optional[str] = None
    ) -> 'BaseResponse[T]':
        """
        创建成功响应
        
        Args:
            data: 响应数据
            message: 成功消息
            
        Returns:
            BaseResponse: 成功响应实例
        """
        return cls(success=True, data=data, message=message or "操作成功")
    
    @classmethod
    def error_response(
        cls, 
        message: str, 
        data: Optional[T] = None
    ) -> 'BaseResponse[T]':
        """
        创建错误响应
        
        Args:
            message: 错误消息
            data: 可选的错误数据
            
        Returns:
            BaseResponse: 错误响应实例
        """
        return cls(success=False, data=data, message=message)


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应模型
    
    用于返回分页数据
    """
    items: List[T]
    total: int
    page: int
    size: int
    total_pages: int


class TokenData(BaseModel):
    """
    令牌数据模型
    
    用于JWT令牌中的负载
    """
    sub: Optional[str] = None
    scopes: List[str] = []
