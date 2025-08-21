"""
自定义异常类
"""
from fastapi import status
from fastapi.exceptions import HTTPException


class AppException(HTTPException):
    """应用基础异常类"""
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = None,
        error_code: str = None,
        **kwargs
    ):
        self.error_code = error_code or f"ERR_{status_code}"
        super().__init__(
            status_code=status_code,
            detail=detail or "An error occurred",
            **kwargs
        )


class ResourceNotFoundError(AppException):
    """资源未找到异常"""
    
    def __init__(self, resource: str = "Resource", **kwargs):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
            error_code="RESOURCE_NOT_FOUND",
            **kwargs
        )


class PermissionDeniedError(AppException):
    """权限不足异常"""
    
    def __init__(self, detail: str = "Permission denied", **kwargs):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="PERMISSION_DENIED",
            **kwargs
        )


class ValidationError(AppException):
    """验证错误异常"""
    
    def __init__(self, detail: str = "Validation error", **kwargs):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="VALIDATION_ERROR",
            **kwargs
        )


class StorageError(AppException):
    """存储错误异常"""
    
    def __init__(self, detail: str = "Storage error", **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="STORAGE_ERROR",
            **kwargs
        )


# 特定于资源的异常
class AssetNotFoundError(ResourceNotFoundError):
    """资源未找到异常"""
    
    def __init__(self, **kwargs):
        super().__init__(resource="Asset", **kwargs)


class ProjectNotFoundError(ResourceNotFoundError):
    """项目未找到异常"""
    
    def __init__(self, **kwargs):
        super().__init__(resource="Project", **kwargs)
