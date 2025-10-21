from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Location, Checkin  # Напряму!
from app.utils.geo import haversine_distance
from app.utils.jwt import decode_access_token
from app.config import settings

router = APIRouter(prefix="/checkins", tags=["checkins"])

# Inline schema
class CheckinCreate(BaseModel):
    location_id: int = Field(..., gt=0)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

# Dependency
async def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> User:  # Прямий імпорт!
    """Отримати поточного користувача"""
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.post("")
async def create_checkin(
    data: CheckinCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Створити check-in"""
    
    # Перевіряємо локацію
    location = db.query(Location).filter(
        Location.id == data.location_id,
        Location.is_active == True
    ).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Розраховуємо відстань
    distance = haversine_distance(
        data.latitude, data.longitude,
        float(location.latitude), float(location.longitude)
    )
    
    if distance > location.radius_meters:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "too_far",
                "message": f"Занадто далеко ({distance}м)",
                "distance_meters": distance
            }
        )
    
    # Перевіряємо cooldown
    cooldown_hours = settings.CHECKIN_COOLDOWN_HOURS
    cooldown_time = datetime.utcnow() - timedelta(hours=cooldown_hours)
    
    last_checkin = db.query(Checkin).filter(
        and_(
            Checkin.user_id == current_user.id,
            Checkin.location_id == data.location_id,
            Checkin.created_at > cooldown_time
        )
    ).first()
    
    if last_checkin:
        next_available = last_checkin.created_at + timedelta(hours=cooldown_hours)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "cooldown_active",
                "message": "Вже чекінились",
                "next_available_at": next_available.isoformat()
            }
        )
    
    # Створюємо check-in
    points = settings.POINTS_PER_CHECKIN
    exp = 10
    
    checkin = Checkin(
        user_id=current_user.id,
        location_id=data.location_id,
        user_latitude=data.latitude,
        user_longitude=data.longitude,
        distance_meters=distance,
        points_earned=points,
        experience_earned=exp
    )
    db.add(checkin)
    
    # Оновлюємо користувача
    current_user.points += points
    current_user.experience += exp
    current_user.total_checkins += 1
    current_user.level = (current_user.experience // 100) + 1
    current_user.last_active_at = datetime.utcnow()
    
    # Оновлюємо локацію
    location.total_checkins += 1
    
    db.commit()
    db.refresh(checkin)
    
    return {
        "success": True,
        "checkin": {
            "id": checkin.id,
            "distance_meters": distance,
            "points_earned": points,
            "created_at": checkin.created_at.isoformat()
        },
        "user_updated": {
            "total_points": current_user.points,
            "total_checkins": current_user.total_checkins,
            "level": current_user.level
        },
        "message": f"🎉 +{points} балів!"
    }


@router.get("/my-history")
async def get_my_checkins(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Історія check-ins"""
    checkins = db.query(Checkin).filter(
        Checkin.user_id == current_user.id
    ).order_by(Checkin.created_at.desc()).offset(skip).limit(limit).all()
    
    return [{
        "id": c.id,
        "location_id": c.location_id,
        "distance_meters": c.distance_meters,
        "points_earned": c.points_earned,
        "created_at": c.created_at.isoformat()
    } for c in checkins]