"""
API 包 - 包含所有API路由和端点
"""

from fastapi import APIRouter

# 创建主API路由器
api_router = APIRouter()

# 在这里导入子路由
# from .v1.endpoints import users, videos, etc.

# 注册API路由
# api_router.include_router(users.router, prefix="/users", tags=["users"])
