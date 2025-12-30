from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import os
import aiofiles
from database import get_db
from crud import get_items, get_item_by_id, create_item, update_item, delete_item, get_user_items
from auth import get_current_user
from schemas import ItemCreate, ItemUpdate, ItemResponse, ItemListResponse, ItemStatusUpdate
from models import User

router = APIRouter(prefix="/items", tags=["商品"])

# 图片上传目录 - 使用绝对路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("", response_model=ItemListResponse)
async def get_items_list(
    skip: int = 0,
    limit: int = 20,
    category: str = None,
    search: str = None,
    sort_by: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    """获取商品列表"""
    items, total = get_items(
        db, 
        skip=skip, 
        limit=limit,
        category=category,
        search=search,
        sort_by=sort_by,
        order=order
    )
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }

@router.get("/categories", response_model=dict)
async def get_categories():
    """获取所有分类"""
    categories = [
        {"id": "electronics", "name": "电子产品", "icon": "📱"},
        {"id": "books", "name": "图书教材", "icon": "📚"},
        {"id": "clothing", "name": "服饰鞋包", "icon": "👕"},
        {"id": "furniture", "name": "家具家居", "icon": "🪑"},
        {"id": "sports", "name": "运动器材", "icon": "⚽"},
        {"id": "beauty", "name": "美妆个护", "icon": "💄"},
        {"id": "food", "name": "食品保健", "icon": "🍎"},
        {"id": "other", "name": "其他", "icon": "📦"}
    ]
    return {"success": True, "data": categories}

@router.get("/my")
async def get_my_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我发布的商品"""
    items = get_user_items(db, current_user.id)
    # 转换为字典列表以避免序列化问题
    items_list = []
    for item in items:
        items_list.append({
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "price": item.price,
            "category": item.category,
            "condition": item.condition,
            "image_url": item.image_url,
            "status": item.status,
            "view_count": item.view_count,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "seller_id": item.seller_id
        })
    return {
        "success": True,
        "data": items_list
    }

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item_detail(item_id: int, db: Session = Depends(get_db)):
    """获取商品详情"""
    item = get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 增加浏览量
    item.view_count += 1
    db.commit()
    
    return item

@router.post("", response_model=dict)
async def create_new_item(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    condition: str = Form("良好"),
    image: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布新商品"""
    # 处理图片上传
    image_url = None
    if image and image.filename:
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{image.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # 同步保存文件
        content = await image.read()
        with open(filepath, 'wb') as f:
            f.write(content)
        
        image_url = f"/static/uploads/{filename}"
    
    item_data = ItemCreate(
        title=title,
        description=description,
        price=price,
        category=category,
        condition=condition
    )
    
    item = create_item(db, item_data, current_user.id)
    
    # 更新图片URL
    if image_url:
        item.image_url = image_url
        db.commit()
    
    return {
        "success": True,
        "message": "发布成功",
        "data": {
            "id": item.id,
            "title": item.title,
            "price": item.price
        }
    }

@router.put("/{item_id}", response_model=dict)
async def update_existing_item(
    item_id: int,
    title: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    category: str = Form(None),
    condition: str = Form(None),
    image: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新商品"""
    item = get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 检查是否是卖家
    if item.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此商品"
        )
    
    # 处理图片上传
    if image and image.filename:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{image.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # 同步保存文件
        content = await image.read()
        with open(filepath, 'wb') as f:
            f.write(content)
        
        image_url = f"/static/uploads/{filename}"
    else:
        image_url = None
    
    # 更新数据
    update_data = ItemUpdate(
        title=title,
        description=description,
        price=price,
        category=category,
        condition=condition
    )
    update_data_dict = update_data.model_dump(exclude_unset=True)
    
    if image_url:
        update_data_dict['image_url'] = image_url
    
    # 过滤None值
    update_data_dict = {k: v for k, v in update_data_dict.items() if v is not None}
    
    item = update_item(db, item, ItemUpdate(**update_data_dict))
    
    return {
        "success": True,
        "message": "更新成功",
        "data": {
            "id": item.id,
            "title": item.title
        }
    }

@router.delete("/{item_id}", response_model=dict)
async def delete_existing_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除商品"""
    item = get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 检查是否是卖家
    if item.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此商品"
        )
    
    delete_item(db, item)
    
    return {
        "success": True,
        "message": "删除成功"
    }

@router.patch("/{item_id}/status", response_model=dict)
async def update_item_status(
    item_id: int,
    status_update: ItemStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新商品状态（用于上架/下架商品）"""
    new_status = status_update.status
    item = get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 检查是否是卖家
    if item.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此商品"
        )
    
    # 验证状态值
    if new_status not in ["active", "inactive", "sold"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的状态值"
        )
    
    # 更新状态
    item.status = new_status
    db.commit()
    db.refresh(item)
    
    status_text = "上架" if new_status == "active" else "下架" if new_status == "inactive" else "售出"
    
    return {
        "success": True,
        "message": f"商品已{status_text}",
        "data": {
            "id": item.id,
            "status": item.status
        }
    }
