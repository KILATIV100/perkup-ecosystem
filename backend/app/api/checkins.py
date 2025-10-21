from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app import models, schemas
from app.utils.geo import haversine_distance
from app.utils.jwt import decode_access_token
from app.config import settings

router = APIRouter(prefix="/checkins", tags=["checkins"])

# Dependency для отримання current user з JWT
async def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> models.User:
    """Отримати поточного користувача з JWT токену"""
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.post("", response_model=schemas.CheckinSuccessResponse)
async def create_checkin(
    data: schemas.CheckinCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Створити новий check-in
    
    Перевіряє:
    1. Чи існує локація
    2. Чи користувач в радіусі локації
    3. Чи не було check-in за останні 12 годин
    """
    
    # 1. Перевіряємо чи існує локація
    location = db.query(models.Location).filter(
        models.Location.id == data.location_id,
        models.Location.is_active == True
    ).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found or inactive")
    
    # 2. Розраховуємо відстань
    distance = haversine_distance(
        data.latitude,
        data.longitude,
        float(location.latitude),
        float(location.longitude)
    )
    
    # Перевіряємо чи користувач в радіусі
    if distance > location.radius_meters:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "too_far",
                "message": f"Ви занадто далеко від локації ({distance}м)",
                "details": {
                    "distance_meters": distance,
                    "max_distance_meters": location.radius_meters
                }
            }
        )
    
    # 3. Перевіряємо cooldown (12 годин)
    cooldown_hours = settings.CHECKIN_COOLDOWN_HOURS
    cooldown_time = datetime.utcnow() - timedelta(hours=cooldown_hours)
    
    last_checkin = db.query(models.Checkin).filter(
        and_(
            models.Checkin.user_id == current_user.id,
            models.Checkin.location_id == data.location_id,
            models.Checkin.created_at > cooldown_time
        )
    ).first()
    
    if last_checkin:
        next_available = last_checkin.created_at + timedelta(hours=cooldown_hours)
        remaining_minutes = int((next_available - datetime.utcnow()).total_seconds() / 60)
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "cooldown_active",
                "message": "Ви вже чекінились тут сьогодні",
                "details": {
                    "last_checkin_at": last_checkin.created_at.isoformat(),
                    "next_available_at": next_available.isoformat(),
                    "cooldown_remaining_minutes": remaining_minutes
                }
            }
        )
    
    # 4. Створюємо check-in
    points_earned = settings.POINTS_PER_CHECKIN
    experience_earned = 10
    
    checkin = models.Checkin(
        user_id=current_user.id,
        location_id=data.location_id,
        user_latitude=data.latitude,
        user_longitude=data.longitude,
        distance_meters=distance,
        points_earned=points_earned,
        experience_earned=experience_earned,
        verification_method='gps',
        is_verified=True
    )
    
    db.add(checkin)
    
    # 5. Оновлюємо користувача
    current_user.points += points_earned
    current_user.experience += experience_earned
    current_user.total_checkins += 1
    current_user.level = (current_user.experience // 100) + 1  # Простий розрахунок левелу
    current_user.last_active_at = datetime.utcnow()
    
    # 6. Оновлюємо статистику локації
    location.total_checkins += 1
    
    db.commit()
    db.refresh(checkin)
    db.refresh(current_user)
    
    # 7. Формуємо відповідь
    return {
        "success": True,
        "checkin": checkin,
        "user_updated": {
            "total_points": current_user.points,
            "total_checkins": current_user.total_checkins,
            "level": current_user.level,
            "level_progress": (current_user.experience % 100)  # % до наступного рівня
        },
        "message": f"🎉 Check-in успішний! +{points_earned} балів"
    }


@router.get("/my-history", response_model=List[schemas.CheckinResponse])
async def get_my_checkins(
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отримати історію check-ins поточного користувача"""
    
    checkins = db.query(models.Checkin).filter(
        models.Checkin.user_id == current_user.id
    ).order_by(
        models.Checkin.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return checkins


@router.get("/can-checkin/{location_id}")
async def can_checkin(
    location_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Перевірити чи може користувач зробити check-in на локації
    (без фактичного створення check-in)
    """
    
    # Перевіряємо локацію
    location = db.query(models.Location).filter(
        models.Location.id == location_id,
        models.Location.is_active == True
    ).first()
    
    if not location:
        return {
            "can_checkin": False,
            "reason": "Location not found or inactive",
            "next_available_at": None
        }
    
    # Перевіряємо cooldown
    cooldown_hours = settings.CHECKIN_COOLDOWN_HOURS
    cooldown_time = datetime.utcnow() - timedelta(hours=cooldown_hours)
    
    last_checkin = db.query(models.Checkin).filter(
        and_(
            models.Checkin.user_id == current_user.id,
            models.Checkin.location_id == location_id,
            models.Checkin.created_at > cooldown_time
        )
    ).first()
    
    if last_checkin:
        next_available = last_checkin.created_at + timedelta(hours=cooldown_hours)
        return {
            "can_checkin": False,
            "reason": "Cooldown period active",
            "last_checkin_at": last_checkin.created_at.isoformat(),
            "next_available_at": next_available.isoformat(),
            "cooldown_remaining_minutes": int((next_available - datetime.utcnow()).total_seconds() / 60)
        }
    
    return {
        "can_checkin": T