from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User  # Прямий імпорт!
from app.api.checkins import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """Отримати профіль поточного користувача"""
    return {
        "id": current_user.id,
        "telegram_id": current_user.telegram_id,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "photo_url": current_user.photo_url,
        "points": current_user.points,
        "level": current_user.level,
        "total_checkins": current_user.total_checkins,
        "best_game_score": current_user.best_game_score,
        "created_at": current_user.created_at.isoformat()
    }


@router.patch("/me")
async def update_my_profile(
    updates: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Оновити профіль"""
    
    allowed_fields = ['username', 'first_name', 'last_name', 'email']
    
    for field, value in updates.items():
        if field in allowed_fields:
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "telegram_id": current_user.telegram_id,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "points": current_user.points,
        "level": current_user.level,
        "created_at": current_user.created_at.isoformat()
    }