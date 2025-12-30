from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List

# ============ 用户相关Schema ============

class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """用户创建模型"""
    password: str
    phone: Optional[str] = None

class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v and len(v) < 3:
            raise ValueError('用户名至少需要3个字符')
        return v

class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    phone: Optional[str]
    avatar: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str

# ============ 商品相关Schema ============

class ItemBase(BaseModel):
    """商品基础模型"""
    title: str
    description: str
    price: float
    category: str
    condition: str = "良好"

class ItemCreate(ItemBase):
    """商品创建模型"""
    pass

class ItemUpdate(BaseModel):
    """商品更新模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    image_url: Optional[str] = None

class ItemResponse(ItemBase):
    """商品响应模型"""
    id: int
    image_url: Optional[str]
    status: str
    view_count: int
    created_at: datetime
    seller: UserResponse
    
    class Config:
        from_attributes = True

class ItemStatusUpdate(BaseModel):
    """商品状态更新模型"""
    status: str

class ItemListResponse(BaseModel):
    """商品列表响应模型"""
    items: List[ItemResponse]
    total: int
    page: int
    page_size: int

# ============ 订单相关Schema ============

class OrderCreate(BaseModel):
    """订单创建模型"""
    item_id: int
    remark: Optional[str] = None

class OrderResponse(BaseModel):
    """订单响应模型"""
    id: int
    status: str
    total_amount: float
    remark: Optional[str]
    created_at: datetime
    item: ItemResponse
    buyer: UserResponse
    
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    """订单列表响应模型"""
    orders: List[OrderResponse]
    total: int

# ============ 消息相关Schema ============

class MessageCreate(BaseModel):
    """消息创建模型"""
    receiver_id: int
    content: str
    item_id: Optional[int] = None

class MessageResponse(BaseModel):
    """消息响应模型"""
    id: int
    content: str
    is_read: bool
    created_at: datetime
    sender: UserResponse
    receiver: UserResponse
    item: Optional[ItemResponse] = None
    
    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    """消息列表响应模型"""
    messages: List[MessageResponse]
    unread_count: int

# ============ Token相关Schema ============

class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token数据模型"""
    username: Optional[str] = None

# ============ 通用响应Schema ============

class ResponseModel(BaseModel):
    """通用响应模型"""
    success: bool
    message: str
    data: Optional[dict] = None
