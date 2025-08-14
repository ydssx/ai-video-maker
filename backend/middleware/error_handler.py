from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback
import time
from typing import Union
import uuid

logger = logging.getLogger(__name__)

class ErrorHandler:
    """统一错误处理器"""
    
    @staticmethod
    def generate_error_id() -> str:
        """生成错误ID用于追踪"""
        return str(uuid.uuid4())[:8]
    
    @staticmethod
    def log_error(error_id: str, error: Exception, request: Request):
        """记录错误信息"""
        logger.error(
            f"Error {error_id}: {type(error).__name__}: {str(error)}",
            extra={
                "error_id": error_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "request_method": request.method,
                "request_url": str(request.url),
                "request_headers": dict(request.headers),
                "traceback": traceback.format_exc()
            }
        )
    
    @staticmethod
    def create_error_response(
        status_code: int,
        error_type: str,
        message: str,
        error_id: str,
        details: Union[dict, None] = None
    ) -> JSONResponse:
        """创建标准化错误响应"""
        content = {
            "error": {
                "type": error_type,
                "message": message,
                "error_id": error_id,
                "timestamp": time.time()
            }
        }
        
        if details:
            content["error"]["details"] = details
        
        return JSONResponse(
            status_code=status_code,
            content=content
        )

async def error_handling_middleware(request: Request, call_next):
    """错误处理中间件"""
    try:
        response = await call_next(request)
        return response
    
    except HTTPException as e:
        # FastAPI HTTP异常
        error_id = ErrorHandler.generate_error_id()
        ErrorHandler.log_error(error_id, e, request)
        
        return ErrorHandler.create_error_response(
            status_code=e.status_code,
            error_type="HTTPException",
            message=e.detail,
            error_id=error_id
        )
    
    except RequestValidationError as e:
        # 请求验证错误
        error_id = ErrorHandler.generate_error_id()
        ErrorHandler.log_error(error_id, e, request)
        
        return ErrorHandler.create_error_response(
            status_code=422,
            error_type="ValidationError",
            message="Request validation failed",
            error_id=error_id,
            details={"validation_errors": e.errors()}
        )
    
    except ValueError as e:
        # 值错误
        error_id = ErrorHandler.generate_error_id()
        ErrorHandler.log_error(error_id, e, request)
        
        return ErrorHandler.create_error_response(
            status_code=400,
            error_type="ValueError",
            message=str(e),
            error_id=error_id
        )
    
    except FileNotFoundError as e:
        # 文件未找到
        error_id = ErrorHandler.generate_error_id()
        ErrorHandler.log_error(error_id, e, request)
        
        return ErrorHandler.create_error_response(
            status_code=404,
            error_type="FileNotFoundError",
            message="Requested resource not found",
            error_id=error_id
        )
    
    except PermissionError as e:
        # 权限错误
        error_id = ErrorHandler.generate_error_id()
        ErrorHandler.log_error(error_id, e, request)
        
        return ErrorHandler.create_error_response(
            status_code=403,
            error_type="PermissionError",
            message="Access denied",
            error_id=error_id
        )
    
    except Exception as e:
        # 其他未预期的错误
        error_id = ErrorHandler.generate_error_id()
        ErrorHandler.log_error(error_id, e, request)
        
        return ErrorHandler.create_error_response(
            status_code=500,
            error_type="InternalServerError",
            message="An unexpected error occurred",
            error_id=error_id
        )