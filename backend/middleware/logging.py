from fastapi import Request
import time
import logging
import json
from typing import Callable

logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next: Callable):
    """请求日志中间件"""
    start_time = time.time()
    
    # 获取客户端信息
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # 记录请求开始
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            "event": "request_started",
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "timestamp": start_time
        }
    )
    
    # 处理请求
    try:
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录请求完成
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "event": "request_completed",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "client_ip": client_ip,
                "timestamp": time.time()
            }
        )
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        return response
    
    except Exception as e:
        # 记录请求失败
        process_time = time.time() - start_time
        
        logger.error(
            f"Request failed: {request.method} {request.url.path} - {type(e).__name__}",
            extra={
                "event": "request_failed",
                "method": request.method,
                "path": request.url.path,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "process_time": process_time,
                "client_ip": client_ip,
                "timestamp": time.time()
            }
        )
        
        # 重新抛出异常让错误处理中间件处理
        raise

def setup_logging():
    """配置日志系统"""
    # 先创建日志目录
    import os
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )