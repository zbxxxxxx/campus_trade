from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    avatar = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    items = relationship("Item", back_populates="seller", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="buyer", foreign_keys="Order.buyer_id")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    received_messages = relationship("Message", back_populates="receiver", foreign_keys="Message.receiver_id")

class Item(Base):
    """商品模型"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    condition = Column(String(20), default="良好")  # 全新/几乎全新/良好/一般
    image_url = Column(String(500), nullable=True)
    status = Column(String(20), default="active")  # active/sold/deleted
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 关系
    seller = relationship("User", back_populates="items")
    order = relationship("Order", back_populates="item", uselist=False)

class Order(Base):
    """订单模型"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20), default="pending")  # pending/completed/cancelled
    total_amount = Column(Float, nullable=False)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    
    # 关系
    buyer = relationship("User", back_populates="orders", foreign_keys=[buyer_id])
    item = relationship("Item", back_populates="order")

class Message(Base):
    """消息模型"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 外键
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    
    # 关系
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="received_messages", foreign_keys=[receiver_id])
    item = relationship("Item", back_populates=None)
