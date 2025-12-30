from sqlalchemy.orm import Session
from models import User, Item, Order, Message
from schemas import UserCreate, ItemCreate, ItemUpdate, OrderCreate, MessageCreate
from auth import get_password_hash, verify_password
from fastapi import HTTPException, status
from typing import List, Optional

# ============ 用户相关CRUD ============

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: UserCreate) -> User:
    """创建新用户"""
    # 检查用户名是否存在
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )
    
    # 检查邮箱是否存在
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        phone=user_data.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户登录"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user: User, user_data: dict) -> User:
    """更新用户信息"""
    for field, value in user_data.items():
        if value is not None:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

# ============ 商品相关CRUD ============

def get_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 20,
    category: str = None,
    search: str = None,
    sort_by: str = "created_at",
    order: str = "desc"
) -> tuple[List[Item], int]:
    """获取商品列表"""
    query = db.query(Item).filter(Item.status == "active")
    
    # 分类筛选
    if category:
        query = query.filter(Item.category == category)
    
    # 搜索
    if search:
        query = query.filter(
            (Item.title.contains(search)) | 
            (Item.description.contains(search))
        )
    
    # 排序
    if order == "desc":
        query = query.order_by(getattr(Item, sort_by).desc())
    else:
        query = query.order_by(getattr(Item, sort_by).asc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    items = query.offset(skip).limit(limit).all()
    
    return items, total

def get_item_by_id(db: Session, item_id: int) -> Optional[Item]:
    """根据ID获取商品"""
    return db.query(Item).filter(Item.id == item_id).first()

def create_item(db: Session, item_data: ItemCreate, seller_id: int) -> Item:
    """创建商品"""
    item = Item(
        **item_data.model_dump(),
        seller_id=seller_id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def update_item(db: Session, item: Item, item_data: ItemUpdate) -> Item:
    """更新商品"""
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

def delete_item(db: Session, item: Item) -> bool:
    """删除商品（软删除）"""
    item.status = "deleted"
    db.commit()
    return True

def get_user_items(db: Session, user_id: int) -> List[Item]:
    """获取用户发布的商品"""
    return db.query(Item).filter(
        Item.seller_id == user_id,
        Item.status != "deleted"
    ).order_by(Item.created_at.desc()).all()

# ============ 订单相关CRUD ============

def create_order(db: Session, order_data: OrderCreate, buyer_id: int) -> Order:
    """创建订单"""
    # 检查商品是否存在
    item = get_item_by_id(db, order_data.item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 检查商品是否已售出
    if item.status == "sold":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="商品已售出"
        )
    
    # 不能购买自己的商品
    if item.seller_id == buyer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能购买自己发布的商品"
        )
    
    # 创建订单
    order = Order(
        buyer_id=buyer_id,
        item_id=item.id,
        total_amount=item.price,
        remark=order_data.remark
    )
    
    # 更新商品状态
    item.status = "sold"
    
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def get_user_orders(db: Session, user_id: int) -> List[Order]:
    """获取用户订单"""
    return db.query(Order).filter(
        Order.buyer_id == user_id
    ).order_by(Order.created_at.desc()).all()

def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    """根据ID获取订单"""
    return db.query(Order).filter(Order.id == order_id).first()

# ============ 消息相关CRUD ============

def create_message(db: Session, message_data: MessageCreate, sender_id: int) -> Message:
    """发送消息"""
    # 检查接收者是否存在
    receiver = get_user_by_id(db, message_data.receiver_id)
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查商品是否存在
    item = None
    if message_data.item_id:
        item = get_item_by_id(db, message_data.item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商品不存在"
            )
    
    message = Message(
        sender_id=sender_id,
        receiver_id=message_data.receiver_id,
        item_id=message_data.item_id,
        content=message_data.content
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_user_messages(db: Session, user_id: int) -> List[Message]:
    """获取用户消息"""
    return db.query(Message).filter(
        (Message.receiver_id == user_id) | 
        (Message.sender_id == user_id)
    ).order_by(Message.created_at.desc()).all()

def get_unread_count(db: Session, user_id: int) -> int:
    """获取未读消息数量"""
    return db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.is_read == False
    ).count()

def mark_message_as_read(db: Session, message_id: int, user_id: int) -> Message:
    """标记消息为已读"""
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.receiver_id == user_id
    ).first()
    
    if message:
        message.is_read = True
        db.commit()
        db.refresh(message)
    
    return message
