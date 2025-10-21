from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.api.checkins import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.UserResponse)
async def get_my_profile(
    current_user: models.User = Depends(get_current_user)
):
    """Отримати профіль поточного користувача"""
    return current_user


@router.patch("/me", response_model=schemas.UserResponse)
async def update_my_profile(
    updates: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Оновити профіль поточного користувача
    
    Дозволені поля: username, first_name, last_name, email
    """
    
    allowed_fields = ['username', 'first_name', 'last_name', 'email']
    
    for field, value in updates.items():
        if field in allowed_fields:
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user