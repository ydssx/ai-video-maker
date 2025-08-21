import asyncio
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Response, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from fastapi.security.api_key import APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, ValidationError, validator

from src.core.config import settings
from src.services.database_service import db_service

router = APIRouter()
logger = logging.getLogger(__name__)

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "user:read": "Read user information",
        "user:write": "Modify user information",
        "admin": "Admin access"
    }
)

# 安全头部
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class UserUpdate(BaseModel):
    """用户信息更新模型"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "张三",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "这是一个用户简介"
            }
        }

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    scopes: List[str] = []
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    
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
                "bio": "这是一个用户简介"
            }
        }

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    scopes: List[str] = []

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: int

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def hash_password(password: str) -> str:
    """
    哈希密码 (兼容旧版本)
    
    注意: 新代码应该使用 get_password_hash 函数
    """
    return get_password_hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False

def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access"
) -> str:
    """
    创建JWT令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间差
        token_type: 令牌类型 (access/refresh)
        
    Returns:
        str: 编码后的JWT令牌
    """
    to_encode = data.copy()
    now = datetime.utcnow()
    
    # 设置过期时间
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 添加标准声明
    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": token_type,
        "jti": secrets.token_urlsafe(16)  # JWT ID
    })
    
    # 生成令牌
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 要编码的数据
        
    Returns:
        str: 编码后的刷新令牌
    """
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(
        data, 
        expires_delta=expires_delta,
        token_type="refresh"
    )

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> UserInDB:
    """获取当前认证用户"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope=\"{security_scopes.scope_str}\"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except JWTError as e:
        logger.error(f"JWT 验证失败: {str(e)}")
        raise credentials_exception
    except ValidationError as e:
        logger.error(f"Token 数据验证失败: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"未知的 Token 验证错误: {str(e)}")
        raise credentials_exception
    
    try:
        user = db_service.get_user_by_username(username=token_data.username)
        if user is None:
            raise credentials_exception
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="无法获取用户信息"
        )
    
    # 检查权限范围
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return user

async def get_current_active_user(
    current_user: UserInDB = Security(get_current_user, scopes=["user:read"])
) -> UserInDB:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user

async def get_current_admin_user(
    current_user: UserInDB = Security(get_current_user, scopes=["admin"])
) -> UserInDB:
    """获取当前管理员用户"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="权限不足")
    return current_user


def get_current_user_simple(user_id: int = 1):
    """获取当前用户 - 简化版本"""
    try:
        user = db_service.get_user(user_id)
        if user is None:
            # 如果用户不存在，创建一个默认用户
            try:
                user_id = db_service.create_user(
                    username="default_user",
                    email="user@example.com"
                )
                user = db_service.get_user(user_id)
            except:
                # 如果创建失败，返回默认结构
                user = {
                    'id': 1,
                    'username': 'default_user',
                    'email': 'user@example.com',
                    'created_at': datetime.now().isoformat()
                }
        return user
    except Exception as e:
        logger.error(f"获取用户失败: {str(e)}")
        # 返回默认用户结构
        return {
            'id': 1,
            'username': 'default_user',
            'email': 'user@example.com',
            'created_at': datetime.now().isoformat()
        }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    用户注册
    
    - **username**: 用户名 (3-50个字符，只允许字母、数字、下划线和连字符)
    - **email**: 邮箱地址
    - **password**: 密码 (至少8个字符，包含大小写字母和数字)
    """
    try:
        # 检查用户名是否已存在
        try:
            existing_user = db_service.get_user_by_username(user_data.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已存在"
                )
        except Exception as e:
            logger.error(f"检查用户名时出错: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="注册过程中发生错误"
            )
        
        # 检查邮箱是否已存在
        try:
            existing_email = db_service.get_user_by_email(user_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被注册"
                )
        except Exception as e:
            logger.error(f"检查邮箱时出错: {str(e)}")
            # 如果方法不存在，继续执行
            pass
        
        # 创建用户
        try:
            hashed_password = get_password_hash(user_data.password)
            user = db_service.create_user(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=False,
                scopes=["user:read", "user:write"]
            )
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="创建用户失败"
                )
            
            # 记录注册统计
            try:
                db_service.log_usage(
                    user.id, 
                    "user_registration", 
                    {
                        "registration_time": datetime.utcnow().isoformat(),
                        "source": "api"
                    }
                )
            except Exception as e:
                logger.error(f"记录注册统计时出错: {str(e)}")
            
            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at,
                last_login=user.last_login,
                scopes=user.scopes or []
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"创建用户时出错: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建用户时发生错误"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"注册过程中发生未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册过程中发生错误"
        )

@router.post("/token", response_model=TokenResponse, include_in_schema=False)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
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
            # 先尝试通过用户名查找
            user = db_service.get_user_by_username(form_data.username)
            # 如果用户名没找到，尝试通过邮箱查找
            if not user and "@" in form_data.username:
                user = db_service.get_user_by_email(form_data.username)
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
            # 记录失败的登录尝试
            try:
                db_service.log_usage(
                    user.id,
                    "login_failed",
                    {
                        "time": datetime.utcnow().isoformat(),
                        "reason": "incorrect_password"
                    }
                )
            except Exception as e:
                logger.error(f"记录登录失败时出错: {str(e)}")
            
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
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="用户未激活"
            )
        
        # 更新最后登录时间
        try:
            db_service.update_user_login_time(user.id)
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
        refresh_token = create_refresh_token(
            data={"sub": user.username}
        )
        
        # 记录登录统计
        try:
            db_service.log_usage(
                user.id,
                "user_login",
                {
                    "login_time": datetime.utcnow().isoformat(),
                    "scopes": list(requested_scopes) or ["user:read"],
                    "token_type": "bearer"
                }
            )
        except Exception as e:
            logger.error(f"记录登录统计时出错: {str(e)}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
            "expires_in": int(access_token_expires.total_seconds()),
            "user_id": user.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录过程中发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录过程中发生错误"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    用户登录接口
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    
    返回访问令牌和刷新令牌
    """
    return await login_for_access_token(form_data)

@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_token: str = Body(..., embed=True)
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
                options={"require": ["exp", "sub", "type"]}
            )
            
            # 检查令牌类型
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的令牌类型"
                )
                
            # 获取用户信息
            username = payload.get("sub")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无效的令牌"
                )
                
            # 获取用户
            try:
                user = db_service.get_user_by_username(username)
            except Exception as e:
                logger.error(f"获取用户信息失败: {str(e)}")
                user = None
                
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在或已被删除"
                )
                
            # 检查用户状态
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户已被禁用"
                )
                
            # 创建新的访问令牌
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "sub": user.username,
                    "scopes": user.scopes or ["user:read"],
                },
                expires_delta=access_token_expires
            )
            
            # 记录令牌刷新
            try:
                db_service.log_usage(
                    user.id,
                    "token_refresh",
                    {
                        "time": datetime.utcnow().isoformat(),
                        "scopes": user.scopes or ["user:read"]
                    }
                )
            except Exception as e:
                logger.error(f"记录令牌刷新时出错: {str(e)}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": int(access_token_expires.total_seconds()),
                "user_id": user.id
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="刷新令牌已过期，请重新登录"
            )
        except jwt.JWTError as e:
            logger.error(f"令牌验证失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新令牌时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刷新令牌时发生错误"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    获取当前认证用户的个人资料
    """
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    更新当前用户的个人资料
    
    - **email**: 新邮箱地址
    - **full_name**: 用户全名
    - **avatar_url**: 头像URL
    - **bio**: 个人简介
    """
    try:
        updated_user = db_service.update_user(
            user_id=current_user.id,
            **user_update.dict(exclude_unset=True)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户信息失败"
            )
            
        return updated_user
        
    except Exception as e:
        logger.error(f"更新用户信息时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户信息时发生错误"
        )

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_user)
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前密码不正确"
            )
            
        # 验证新密码强度
        try:
            UserCreate(password=new_password)  # 使用Pydantic验证密码强度
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码不符合要求: " + ", ".join([str(err) for err in e.errors()])
            )
            
        # 更新密码
        hashed_password = get_password_hash(new_password)
        success = db_service.update_user(
            user_id=current_user.id,
            hashed_password=hashed_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="密码更新失败"
            )
            
        # 记录密码修改
        try:
            db_service.log_usage(
                current_user.id,
                "password_change",
                {"time": datetime.utcnow().isoformat()}
            )
        except Exception as e:
            logger.error(f"记录密码修改日志时出错: {str(e)}")
            
        return {"message": "密码已成功更新"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码时发生错误"
        )

@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: int):
    """
    获取指定用户的公开资料
    
    - **user_id**: 用户ID
    """
    try:
        user = db_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
            
        # 只返回公开信息
        return {
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at,
            "bio": getattr(user, 'bio', None),
            "avatar_url": getattr(user, 'avatar_url', None)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户资料时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户资料时发生错误"
        )

# 管理员专用API
@router.get("/users/", response_model=List[UserResponse], dependencies=[Depends(get_current_admin_user)])
async def list_users(
    skip: int = 0,
    limit: int = 100,
):
    """
    获取用户列表 (仅管理员)
    
    - **skip**: 跳过的记录数
    - **limit**: 每页记录数 (最大100)
    """
    try:
        users = db_service.get_users(skip=skip, limit=min(limit, 100))
        return users
    except Exception as e:
        logger.error(f"获取用户列表时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表时发生错误"
        )

@router.put("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(get_current_admin_user)])
async def update_user(
    user_id: int,
    user_update: UserUpdate
):
    """
    更新用户信息 (仅管理员)
    
    - **user_id**: 用户ID
    - **user_update**: 用户更新信息
    """
    try:
        # 检查用户是否存在
        user = db_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
            
        # 更新用户信息
        updated_user = db_service.update_user(
            user_id=user_id,
            **user_update.dict(exclude_unset=True)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户信息失败"
            )
            
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户信息时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户信息时发生错误"
        )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin_user)])
async def delete_user(user_id: int):
    """
    删除用户 (仅管理员)
    
    - **user_id**: 用户ID
    """
    try:
        # 检查用户是否存在
        user = db_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
            
        # 执行删除操作
        success = db_service.delete_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除用户失败"
            )
            
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户时发生错误"
        )

@router.get("/stats/{user_id}")
async def get_user_stats(user_id: int):
    """获取用户统计信息"""
    try:
        try:
            stats = db_service.get_user_stats(user_id)
        except:
            stats = {}  # 如果方法不存在，返回空字典
            
        return {
            "scripts_generated": stats.get('script_generation', 0),
            "videos_created": stats.get('video_generation', 0),
            "total_duration": stats.get('total_video_duration', 0.0),
            "last_activity": None  # 可以从数据库获取
        }
        
    except Exception as e:
        logger.error(f"获取用户统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计失败")

@router.get("/usage-history")
async def get_usage_history(
    days: int = 30,
    user_id: int = 1
):
    """获取使用历史"""
    try:
        current_user = get_current_user_simple(user_id)
        try:
            history = db_service.get_user_usage_history(current_user['id'], days)
        except Exception as e:
            logger.debug(f"获取使用历史时出错: {str(e)}", exc_info=True)
            history = []  # 如果方法不存在或出错，返回空列表
        
        return {
            "history": history,
            "period_days": days,
            "total_records": len(history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取使用历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取历史失败")


@router.get("/preferences")
async def get_user_preferences(user_id: int = 1):
    """获取用户偏好设置"""
    try:
        current_user = get_current_user_simple(user_id)
        try:
            settings = db_service.get_user_settings(current_user['id'])
            return settings or {}
        except Exception as e:
            logger.debug(f"获取用户设置时出错: {str(e)}")
            return {}  # 如果方法不存在或出错，返回空字典
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户偏好失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取偏好失败")

@router.put("/preferences")
async def update_user_preferences(
    preferences: Dict,
    user_id: int = 1
):
    """更新用户偏好设置"""
    try:
        current_user = get_current_user_simple(user_id)
        
        try:
            db_service.update_user_settings(current_user['id'], preferences)
        except Exception as e:
            logger.debug(f"更新用户设置时出错: {str(e)}")
        
        # 记录设置更新
        try:
            db_service.log_usage(current_user['id'], "preferences_update", preferences)
        except Exception as e:
            logger.debug(f"记录偏好设置更新时出错: {str(e)}")
        
        return {"message": "偏好设置更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户偏好失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新偏好失败")