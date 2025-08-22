"""
基础仓库类

提供所有仓库共用的CRUD操作。
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.models.base import BaseModel as Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    基础CRUD仓库类
    
    Args:
        model: SQLAlchemy模型类
    """
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        根据ID获取单个记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            Optional[ModelType]: 找到的记录或None
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        获取多条记录（分页）
        
        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            List[ModelType]: 记录列表
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        创建新记录
        
        Args:
            db: 数据库会话
            obj_in: 包含创建数据的Pydantic模型
            
        Returns:
            ModelType: 创建的记录
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        更新记录
        
        Args:
            db: 数据库会话
            db_obj: 要更新的数据库记录
            obj_in: 包含更新数据的Pydantic模型或字典
            
        Returns:
            ModelType: 更新后的记录
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        删除记录
        
        Args:
            db: 数据库会话
            id: 要删除的记录ID
            
        Returns:
            ModelType: 被删除的记录
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
    
    def get_by_field(
        self, db: Session, *, field: str, value: Any, case_sensitive: bool = True
    ) -> Optional[ModelType]:
        """
        根据字段值获取单个记录
        
        Args:
            db: 数据库会话
            field: 字段名
            value: 字段值
            case_sensitive: 是否区分大小写
            
        Returns:
            Optional[ModelType]: 找到的记录或None
        """
        query = db.query(self.model)
        
        if not case_sensitive and isinstance(value, str):
            query = query.filter(
                getattr(self.model, field).ilike(f"%{value}%")
            )
        else:
            query = query.filter(getattr(self.model, field) == value)
            
        return query.first()
    
    def get_multi_by_field(
        self,
        db: Session,
        *,
        field: str,
        value: Any,
        skip: int = 0,
        limit: int = 100,
        case_sensitive: bool = True
    ) -> List[ModelType]:
        """
        根据字段值获取多条记录
        
        Args:
            db: 数据库会话
            field: 字段名
            value: 字段值
            skip: 跳过的记录数
            limit: 返回的最大记录数
            case_sensitive: 是否区分大小写
            
        Returns:
            List[ModelType]: 记录列表
        """
        query = db.query(self.model)
        
        if not case_sensitive and isinstance(value, str):
            query = query.filter(
                getattr(self.model, field).ilike(f"%{value}%")
            )
        else:
            query = query.filter(getattr(self.model, field) == value)
            
        return query.offset(skip).limit(limit).all()
