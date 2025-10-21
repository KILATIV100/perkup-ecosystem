from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("")  # БЕЗ response_model
async def get_locations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Отримати список всіх активних локацій"""
    locations = db.query(models.Location).filter(
        models.Location.is_active == True
    ).offset(skip).limit(limit).all()
    
    return [{
        "id": loc.id,
        "name": loc.name,
        "slug": loc.slug,
        "address": loc.address,
        "city": loc.city,
        "latitude": float(loc.latitude),
        "longitude": float(loc.longitude),
        "radius_meters": loc.radius_meters,
        "description": loc.description,
        "phone": loc.phone,
        "is_active": loc.is_active,
        "total_checkins": loc.total_checkins,
        "created_at": loc.created_at.isoformat()
    } for loc in locations]

@router.get("/{location_id}")  # БЕЗ response_model
async def get_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    """Отримати деталі конкретної локації"""
    location = db.query(models.Location).filter(
        models.Location.id == location_id,
        models.Location.is_active == True
    ).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return {
        "id": location.id,
        "name": location.name,
        "slug": location.slug,
        "address": location.address,
        "city": location.city,
        "latitude": float(location.latitude),
        "longitude": float(location.longitude),
        "radius_meters": location.radius_meters,
        "description": location.description,
        "phone": location.phone,
        "is_active": location.is_active,
        "total_checkins": location.total_checkins,
        "created_at": location.created_at.isoformat()
    }