from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from crud import create_message, get_user_messages, get_unread_count, mark_message_as_read, get_user_by_id
from auth import get_current_user
from schemas import MessageCreate, MessageResponse, MessageListResponse
from models import User

router = APIRouter(prefix="/messages", tags=["消息"])

@router.get("", response_model=MessageListResponse)
async def get_my_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的消息"""
    messages = get_user_messages(db, current_user.id)
    unread_count = get_unread_count(db, current_user.id)
    return {
        "messages": messages,
        "unread_count": unread_count
    }

@router.post("", response_model=dict)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送消息"""
    try:
        message = create_message(db, message_data, current_user.id)
        return {
            "success": True,
            "message": "消息已发送",
            "data": {
                "message_id": message.id,
                "created_at": message.created_at.isoformat()
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送失败: {str(e)}"
        )

@router.put("/{message_id}/read", response_model=dict)
async def mark_as_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记消息为已读"""
    message = mark_message_as_read(db, message_id, current_user.id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    return {
        "success": True,
        "message": "已标记为已读"
    }

@router.get("/unread", response_model=dict)
async def get_unread_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取未读消息数量"""
    count = get_unread_count(db, current_user.id)
    return {
        "success": True,
        "data": {"unread_count": count}
    }
