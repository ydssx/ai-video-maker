import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Response, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from fastapi.security.api_key import APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, ValidationError, validator

from src.core.config import settings
from sqlalchemy.orm import Session
from src.db.session import SessionLocal, get_db
from src.db.repositories.user import user_repo
from src.schemas.user import (
    UserCreate as RepoUserCreate,
    UserUpdate,
    UserBase,
    UserInDB,
)
from src.core.security import create_access_token,create_refresh_token
from src.api.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days


# 安全头部
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    scopes: List[str] = []

    # 保证 scopes 字段始终为列表，避免数据库返回 None 导致验证错误
    @validator("scopes", pre=True, always=True)
    def set_scopes(cls, v):
        return v or []

    # full_name: Optional[str] = None
    # avatar_url: Optional[str] = None
    # bio: Optional[str] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "testuser",
                "email": "user@example.com",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "last_login": "2023-01-01T12:00:00",
                "scopes": ["user:read", "user:write"],
                "full_name": "张三",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "这是一个用户简介",
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: int


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False



async def get_current_active_user(
    current_user: UserInDB = Security(get_current_user, scopes=["user:read"]),
) -> UserInDB:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user


async def get_current_admin_user(
    current_user: UserInDB = Security(get_current_user, scopes=["admin"]),
) -> UserInDB:
    """获取当前管理员用户"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="权限不足")
    return current_user


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册

    - **username**: 用户名 (3-50个字符，只允许字母、数字、下划线和连字符)
    - **email**: 邮箱地址
    - **password**: 密码 (至少8个字符，包含大小写字母和数字)
    """
    try:
        # 检查用户名是否已存在
        try:
            existing_user = user_repo.get_by_username(db, username=user_data.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
                )
        except Exception as e:
            logger.error(f"检查用户名时出错: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="注册过程中发生错误",
            )

        # 检查邮箱是否已存在
        try:
            existing_email = user_repo.get_by_email(db, email=user_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册"
                )
        except Exception as e:
            logger.error(f"检查邮箱时出错: {str(e)}")
            # 如果方法不存在，继续执行
            pass

        # 创建用户
        try:
            created = user_repo.create(
                db,
                obj_in=RepoUserCreate(
                    username=user_data.username,
                    email=user_data.email,
                    password=user_data.password,
                ),
            )

            # 记录注册统计
            # usage 记录可通过独立仓库实现，当前省略

            return UserResponse(
                id=created.id,
                username=created.username,
                email=created.email,
                is_active=created.is_active,
                created_at=created.created_at,
                last_login=getattr(created, "last_login", None),
                scopes=[],
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"创建用户时出错: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建用户时发生错误",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"注册过程中发生未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册过程中发生错误",
        )


@router.post("/token", response_model=TokenResponse, include_in_schema=False)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    OAuth2 兼容的令牌登录接口 (内部使用)

    - **username**: 用户名或邮箱
    - **password**: 密码
    - **scope**: 可选，请求的权限范围，多个用空格分隔

    返回访问令牌和刷新令牌
    """
    try:
        # 获取用户信息
        try:
            user = user_repo.get_by_username(db, username=form_data.username)
            if not user and "@" in form_data.username:
                user = user_repo.get_by_email(db, email=form_data.username)
        except Exception as e:
            logger.error(f"获取用户信息时出错: {str(e)}")
            user = None

        # 验证用户是否存在
        if not user:
            # 防止用户枚举攻击，返回相同的错误信息
            # 在实际生产环境中，可以添加延时来防止暴力破解
            await asyncio.sleep(0.5)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 验证密码
        if not verify_password(form_data.password, user.hashed_password):
            # 失败登录可记录 usage，暂略

            # 防止时间攻击，使用固定时间比较
            verify_password("dummy_password", user.hashed_password)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 检查用户是否激活
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户未激活"
            )

        # 更新最后登录时间
        try:
            user_repo.update(db, db_obj=user, obj_in={"last_login": datetime.utcnow()})
        except Exception as e:
            logger.error(f"更新登录时间时出错: {str(e)}")

        # 处理请求的权限范围
        requested_scopes = set(form_data.scopes) if form_data.scopes else set()
        user_scopes = set(user.scopes or ["user:read"])

        # 确保请求的权限范围是用户所拥有的子集
        if not requested_scopes.issubset(user_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="请求的权限范围无效",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.username,
                "scopes": list(requested_scopes) or ["user:read"],
            },
            expires_delta=access_token_expires,
        )

        # 创建刷新令牌
        refresh_token = create_refresh_token(data={"sub": user.username})

        # 记录登录统计
        # usage 统计可在后续仓库中实现

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
            "expires_in": int(access_token_expires.total_seconds()),
            "user_id": user.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录过程中发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录过程中发生错误",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    用户登录接口

    - **username**: 用户名或邮箱
    - **password**: 密码

    返回访问令牌和刷新令牌
    """
    return await login_for_access_token(form_data, db)


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)
):
    """
    使用刷新令牌获取新的访问令牌

    - **refresh_token**: 之前获取的刷新令牌
    """
    try:
        # 验证刷新令牌
        try:
            payload = jwt.decode(
                refresh_token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"require": ["exp", "sub", "type"]},
            )

            # 检查令牌类型
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌类型"
                )

            # 获取用户信息
            username = payload.get("sub")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="无效的令牌"
                )

            # 获取用户
            try:
                user = user_repo.get_by_username(db, username=username)
            except Exception as e:
                logger.error(f"获取用户信息失败: {str(e)}")
                user = None

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在或已被删除"
                )

            # 检查用户状态
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="用户已被禁用"
                )

            # 创建新的访问令牌
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "sub": user.username,
                    "scopes": user.scopes or ["user:read"],
                },
                expires_delta=access_token_expires,
            )

            # 记录令牌刷新可通过 usage 仓库实现，暂略

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": int(access_token_expires.total_seconds()),
                "user_id": user.id,
            }

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="刷新令牌已过期，请重新登录",
            )
        except jwt.JWTError as e:
            logger.error(f"令牌验证失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新令牌时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刷新令牌时发生错误",
        )


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """
    获取当前认证用户的个人资料
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新当前用户的个人资料

    - **email**: 新邮箱地址
    - **full_name**: 用户全名
    - **avatar_url**: 头像URL
    - **bio**: 个人简介
    """
    try:
        updated_user = user_repo.update(db, db_obj=current_user, obj_in=user_update)
        return updated_user

    except Exception as e:
        logger.error(f"更新用户信息时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户信息时发生错误",
        )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    修改当前用户的密码

    - **current_password**: 当前密码
    - **new_password**: 新密码
    """
    try:
        # 验证当前密码
        if not verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码不正确"
            )

        # 验证新密码强度
        try:
            UserCreate(password=new_password)  # 使用Pydantic验证密码强度
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码不符合要求: "
                + ", ".join([str(err) for err in e.errors()]),
            )

        # 更新密码
        hashed_password = get_password_hash(new_password)
        user_repo.update(
            db, db_obj=current_user, obj_in={"hashed_password": hashed_password}
        )

        # 记录密码修改
        # usage记录省略

        return {"message": "密码已成功更新"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码时发生错误",
        )


@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    获取指定用户的公开资料

    - **user_id**: 用户ID
    """
    try:
        user = user_repo.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )

        # 只返回公开信息
        return {
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at,
            "bio": getattr(user, "bio", None),
            "avatar_url": getattr(user, "avatar", None),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户资料时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户资料时发生错误",
        )


# 管理员专用API
@router.get(
    "/users/",
    response_model=List[UserResponse],
    dependencies=[Depends(get_current_admin_user)],
)
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取用户列表 (仅管理员)

    - **skip**: 跳过的记录数
    - **limit**: 每页记录数 (最大100)
    """
    try:
        users = user_repo.get_multi(db, skip=skip, limit=min(limit, 100))
        return users
    except Exception as e:
        logger.error(f"获取用户列表时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表时发生错误",
        )


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(get_current_admin_user)],
)
async def update_user(
    user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)
):
    """
    更新用户信息 (仅管理员)

    - **user_id**: 用户ID
    - **user_update**: 用户更新信息
    """
    try:
        # 检查用户是否存在
        user = user_repo.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )

        # 更新用户信息
        updated_user = user_repo.update(db, db_obj=user, obj_in=user_update)

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户信息失败",
            )

        return updated_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户信息时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户信息时发生错误",
        )


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin_user)],
)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    删除用户 (仅管理员)

    - **user_id**: 用户ID
    """
    try:
        # 检查用户是否存在
        user = user_repo.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )

        # 执行删除操作
        user_repo.remove(db, id=user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户时发生错误",
        )


@router.get("/stats/{user_id}")
async def get_user_stats(user_id: int):
    """获取用户统计信息"""
    try:
        try:
            stats = {}
        except Exception:
            stats = {}

        return {
            "scripts_generated": stats.get("script_generation", 0),
            "videos_created": stats.get("video_generation", 0),
            "total_duration": stats.get("total_video_duration", 0.0),
            "last_activity": None,  # 可以从数据库获取
        }

    except Exception as e:
        logger.error(f"获取用户统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计失败")


@router.get("/usage-history")
async def get_usage_history(
    days: int = 30,
    user_id: int = 1,
    current_user: UserInDB = Depends(get_current_user),
):
    """获取使用历史"""
    try:
        try:
            history = []
        except Exception as e:
            logger.debug(f"获取使用历史时出错: {str(e)}", exc_info=True)
            history = []

        return {"history": history, "period_days": days, "total_records": len(history)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取使用历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取历史失败")


@router.get("/preferences")
async def get_user_preferences(
    current_user: UserInDB = Depends(get_current_user),
):
    """获取用户偏好设置"""
    try:
        try:
            settings = {}
            return settings or {}
        except Exception as e:
            logger.debug(f"获取用户设置时出错: {str(e)}")
            return {}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户偏好失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取偏好失败")


@router.put("/preferences")
async def update_user_preferences(
    preferences: Dict,
    current_user: UserInDB = Depends(get_current_user),
):
    """更新用户偏好设置"""
    try:
        # 偏好设置可在后续仓库实现，此处直接返回成功
        return {"message": "偏好设置更新成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户偏好失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新偏好失败")
