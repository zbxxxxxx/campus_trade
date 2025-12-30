from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from crud import create_order, get_user_orders, get_order_by_id, get_item_by_id
from auth import get_current_user
from schemas import OrderCreate, OrderResponse, OrderListResponse
from models import User

router = APIRouter(prefix="/orders", tags=["订单"])

@router.post("", response_model=dict)
async def create_new_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建订单"""
    try:
        order = create_order(db, order_data, current_user.id)
        return {
            "success": True,
            "message": "购买成功",
            "data": {
                "order_id": order.id,
                "item_id": order.item_id,
                "total_amount": order.total_amount
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建订单失败: {str(e)}"
        )

@router.get("", response_model=OrderListResponse)
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的订单"""
    orders = get_user_orders(db, current_user.id)
    return {
        "orders": orders,
        "total": len(orders)
    }

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单详情"""
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 检查是否是订单买家
    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此订单"
        )
    
    return order
