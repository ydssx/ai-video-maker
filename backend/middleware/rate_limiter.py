from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from collections import defaultdict, deque
from typing import Dict, Deque
import asyncio
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """简单的内存基础限流器"""
    
    def __init__(self):
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """检查是否允许请求"""
        async with self.lock:
            now = time.time()
            window_start = now - window_seconds
            
            # 清理过期的请求记录
            while self.requests[key] and self.requests[key][0] < window_start:
                self.requests[key].popleft()
            
            # 检查是否超过限制
            if len(self.requests[key]) >= max_requests:
                return False
            
            # 记录当前请求
            self.requests[key].append(now)
            return True
    
    async def cleanup_old_records(self):
        """清理旧的请求记录"""
        async with self.lock:
            now = time.time()
            keys_to_remove = []
            
            for key, requests in self.requests.items():
                # 清理1小时前的记录
                while requests and requests[0] < now - 3600:
                    requests.popleft()
                
                # 如果队列为空，标记删除
                if not requests:
                    keys_to_remove.append(key)
            
            # 删除空的记录
            for key in keys_to_remove:
                del self.requests[key]

# 全局限流器实例
rate_limiter = RateLimiter()

def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    # 检查代理头
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 回退到直接连接IP
    return request.client.host if request.client else "unknown"

async def rate_limit_middleware(request: Request, call_next):
    """限流中间件"""
    # 获取客户端标识
    client_ip = get_client_ip(request)
    
    # 不同端点的限流配置
    rate_limits = {
        "/api/video/create": (5, 60),      # 每分钟5次
        "/api/video/generate": (5, 60),    # 每分钟5次
        "/api/script/generate": (10, 60),  # 每分钟10次
        "/api/user-assets/upload": (20, 60), # 每分钟20次
        "default": (100, 60)               # 默认每分钟100次
    }
    
    # 获取当前路径的限流配置
    path = request.url.path
    max_requests, window_seconds = rate_limits.get(path, rate_limits["default"])
    
    # 构建限流键
    rate_limit_key = f"{client_ip}:{path}"
    
    # 检查是否允许请求
    if not await rate_limiter.is_allowed(rate_limit_key, max_requests, window_seconds):
        logger.warning(f"Rate limit exceeded for {client_ip} on {path}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {max_requests} per {window_seconds} seconds",
                "retry_after": window_seconds
            },
            headers={"Retry-After": str(window_seconds)}
        )
    
    # 继续处理请求
    response = await call_next(request)
    
    # 添加限流信息到响应头
    remaining = max_requests - len(rate_limiter.requests[rate_limit_key])
    response.headers["X-RateLimit-Limit"] = str(max_requests)
    response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + window_seconds))
    
    return response