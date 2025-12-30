from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models import User
from crud import create_user, authenticate_user, get_user_by_username, update_user, get_user_by_id
from auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import UserCreate, UserResponse, UserUpdate, Token

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        user = create_user(db, user_data)
        return {
            "success": True,
            "message": "注册成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=dict)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    # 检查用户名是否被占用
    if user_data.username and user_data.username != current_user.username:
        if get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被注册"
            )
    
    update_data = user_data.model_dump(exclude_unset=True)
    user = update_user(db, current_user, update_data)
    
    return {
        "success": True,
        "message": "更新成功",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone
        }
    }

@router.get("/users/{user_id}", response_model=dict)
async def get_user_by_id_endpoint(user_id: int, db: Session = Depends(get_db)):
    """根据ID获取用户信息"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {
        "success": True,
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone
        }
    }
