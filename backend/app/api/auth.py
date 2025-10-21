from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils.telegram import validate_telegram_init_data
from app.utils.jwt import create_access_token
from app.config import settings
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/telegram", response_model=schemas.AuthResponse)
async def telegram_auth(
    data: schemas.TelegramAuthRequest,
    db: Session = Depends(get_db)
):
    """Авторизація через Telegram Mini App"""
    
    # Валідуємо init_data
    user_data = validate_telegram_init_data(
        data.init_data,
        settings.TELEGRAM_BOT_TOKEN
    )
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid Telegram authentication data")
    
    telegram_id = user_data.get('id')
    
    # Шукаємо або створюємо користувача
    user = db.query(models.User).filter(
        models.User.telegram_id == telegram_id
    ).first()
    
    if not user:
        # Створюємо нового користувача
        user = models.User(
            telegram_id=telegram_id,
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            photo_url=user_data.get('photo_url'),
            language_code=user_data.get('language_code', 'uk')
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Оновлюємо дані користувача
        user.username = user_data.get('username')
        user.first_name = user_data.get('first_name')
        user.last_name = user_data.get('last_name')
        user.photo_url = user_data.get('photo_url')
        user.last_active_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    
    # Створюємо JWT token
    access_token = create_access_token(
        data={"user_id": user.id, "telegram_id": telegram_id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_DAYS * 86400,
        "user": user
    }