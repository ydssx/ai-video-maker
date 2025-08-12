from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/api/projects", tags=["projects"])

# 项目存储目录
PROJECTS_DIR = Path("data/projects")
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

# 项目索引文件
PROJECTS_INDEX_FILE = PROJECTS_DIR / "index.json"

class ProjectData(BaseModel):
    name: str
    description: Optional[str] = ""
    category: str = "general"
    tags: List[str] = []
    script: Dict[str, Any]
    video_config: Dict[str, Any] = {}
    thumbnail: Optional[Dict[str, Any]] = None
    created_time: Optional[str] = None
    updated_time: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    updated_time: Optional[str] = None

def load_projects_index():
    """加载项目索引"""
    if PROJECTS_INDEX_FILE.exists():
        try:
            with open(PROJECTS_INDEX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_projects_index(index):
    """保存项目索引"""
    with open(PROJECTS_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def load_project_data(project_id):
    """加载项目详细数据"""
    project_file = PROJECTS_DIR / f"{project_id}.json"
    if not project_file.exists():
        return None
    
    try:
        with open(project_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def save_project_data(project_id, project_data):
    """保存项目详细数据"""
    project_file = PROJECTS_DIR / f"{project_id}.json"
    with open(project_file, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, ensure_ascii=False, indent=2)

@router.post("/save")
async def save_project(project_data: ProjectData):
    """保存项目"""
    
    # 生成项目ID
    project_id = str(uuid.uuid4())
    current_time = datetime.now().isoformat()
    
    # 准备项目数据
    project_dict = project_data.dict()
    project_dict['id'] = project_id
    project_dict['created_time'] = project_dict.get('created_time') or current_time
    project_dict['updated_time'] = project_dict.get('updated_time') or current_time
    
    try:
        # 保存项目详细数据
        save_project_data(project_id, project_dict)
        
        # 更新项目索引
        index = load_projects_index()
        index[project_id] = {
            'id': project_id,
            'name': project_dict['name'],
            'description': project_dict['description'],
            'category': project_dict['category'],
            'tags': project_dict['tags'],
            'thumbnail': project_dict['thumbnail'],
            'created_time': project_dict['created_time'],
            'updated_time': project_dict['updated_time']
        }
        save_projects_index(index)
        
        return {
            "success": True,
            "message": "项目保存成功",
            "project": project_dict
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存项目失败: {str(e)}")

@router.get("/list")
async def list_projects(
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """获取项目列表"""
    
    try:
        index = load_projects_index()
        projects = list(index.values())
        
        # 按分类筛选
        if category and category != 'all':
            projects = [p for p in projects if p.get('category') == category]
        
        # 按更新时间排序
        projects.sort(key=lambda x: x.get('updated_time', ''), reverse=True)
        
        # 分页
        total = len(projects)
        projects = projects[offset:offset + limit]
        
        return {
            "success": True,
            "projects": projects,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目列表失败: {str(e)}")

@router.get("/{project_id}")
async def get_project(project_id: str):
    """获取项目详情"""
    
    project_data = load_project_data(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    return {
        "success": True,
        "project": project_data
    }

@router.put("/{project_id}")
async def update_project(project_id: str, update_data: ProjectUpdate):
    """更新项目信息"""
    
    # 检查项目是否存在
    project_data = load_project_data(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    try:
        # 更新项目数据
        update_dict = update_data.dict(exclude_unset=True)
        update_dict['updated_time'] = datetime.now().isoformat()
        
        for key, value in update_dict.items():
            if value is not None:
                project_data[key] = value
        
        # 保存更新后的项目数据
        save_project_data(project_id, project_data)
        
        # 更新索引
        index = load_projects_index()
        if project_id in index:
            index[project_id].update({
                'name': project_data['name'],
                'description': project_data['description'],
                'category': project_data['category'],
                'tags': project_data['tags'],
                'updated_time': project_data['updated_time']
            })
            save_projects_index(index)
        
        return {
            "success": True,
            "message": "项目更新成功",
            "project": project_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新项目失败: {str(e)}")

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    
    # 检查项目是否存在
    project_data = load_project_data(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    try:
        # 删除项目文件
        project_file = PROJECTS_DIR / f"{project_id}.json"
        if project_file.exists():
            project_file.unlink()
        
        # 从索引中删除
        index = load_projects_index()
        if project_id in index:
            del index[project_id]
            save_projects_index(index)
        
        return {
            "success": True,
            "message": "项目删除成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除项目失败: {str(e)}")

@router.get("/categories/list")
async def list_categories():
    """获取项目分类列表"""
    
    try:
        index = load_projects_index()
        categories = set()
        
        for project in index.values():
            if project.get('category'):
                categories.add(project['category'])
        
        return {
            "success": True,
            "categories": sorted(list(categories))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类列表失败: {str(e)}")

@router.get("/tags/list")
async def list_tags():
    """获取项目标签列表"""
    
    try:
        index = load_projects_index()
        tags = set()
        
        for project in index.values():
            if project.get('tags'):
                tags.update(project['tags'])
        
        return {
            "success": True,
            "tags": sorted(list(tags))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取标签列表失败: {str(e)}")

@router.post("/{project_id}/duplicate")
async def duplicate_project(project_id: str):
    """复制项目"""
    
    # 获取原项目数据
    original_project = load_project_data(project_id)
    if not original_project:
        raise HTTPException(status_code=404, detail="原项目不存在")
    
    try:
        # 生成新项目ID
        new_project_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # 创建新项目数据
        new_project = original_project.copy()
        new_project['id'] = new_project_id
        new_project['name'] = f"{original_project['name']} - 副本"
        new_project['created_time'] = current_time
        new_project['updated_time'] = current_time
        
        # 保存新项目
        save_project_data(new_project_id, new_project)
        
        # 更新索引
        index = load_projects_index()
        index[new_project_id] = {
            'id': new_project_id,
            'name': new_project['name'],
            'description': new_project['description'],
            'category': new_project['category'],
            'tags': new_project['tags'],
            'thumbnail': new_project['thumbnail'],
            'created_time': new_project['created_time'],
            'updated_time': new_project['updated_time']
        }
        save_projects_index(index)
        
        return {
            "success": True,
            "message": "项目复制成功",
            "project": new_project
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"复制项目失败: {str(e)}")

@router.get("/stats/overview")
async def get_project_stats():
    """获取项目统计信息"""
    
    try:
        index = load_projects_index()
        projects = list(index.values())
        
        # 基本统计
        total_projects = len(projects)
        
        # 分类统计
        category_stats = {}
        for project in projects:
            category = project.get('category', 'general')
            category_stats[category] = category_stats.get(category, 0) + 1
        
        # 标签统计
        tag_stats = {}
        for project in projects:
            for tag in project.get('tags', []):
                tag_stats[tag] = tag_stats.get(tag, 0) + 1
        
        # 时间统计
        recent_projects = [
            p for p in projects 
            if (datetime.now() - datetime.fromisoformat(p.get('updated_time', '2000-01-01T00:00:00'))).days <= 7
        ]
        
        return {
            "success": True,
            "stats": {
                "total_projects": total_projects,
                "category_stats": category_stats,
                "tag_stats": dict(sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
                "recent_projects_count": len(recent_projects)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.post("/export/{project_id}")
async def export_project(project_id: str):
    """导出项目数据"""
    
    project_data = load_project_data(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    try:
        # 准备导出数据
        export_data = {
            "project": project_data,
            "export_time": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        return {
            "success": True,
            "export_data": export_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出项目失败: {str(e)}")

@router.post("/import")
async def import_project(import_data: Dict[str, Any]):
    """导入项目数据"""
    
    try:
        if "project" not in import_data:
            raise HTTPException(status_code=400, detail="无效的导入数据")
        
        project_data = import_data["project"]
        
        # 生成新的项目ID
        new_project_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        project_data['id'] = new_project_id
        project_data['name'] = f"{project_data.get('name', '导入项目')} - 导入"
        project_data['created_time'] = current_time
        project_data['updated_time'] = current_time
        
        # 保存项目
        save_project_data(new_project_id, project_data)
        
        # 更新索引
        index = load_projects_index()
        index[new_project_id] = {
            'id': new_project_id,
            'name': project_data['name'],
            'description': project_data.get('description', ''),
            'category': project_data.get('category', 'general'),
            'tags': project_data.get('tags', []),
            'thumbnail': project_data.get('thumbnail'),
            'created_time': project_data['created_time'],
            'updated_time': project_data['updated_time']
        }
        save_projects_index(index)
        
        return {
            "success": True,
            "message": "项目导入成功",
            "project": project_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入项目失败: {str(e)}")