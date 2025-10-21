from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("", response_model=List[schemas.LocationResponse])
async def get_locations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Отримати список всіх активних локацій"""
    locations = db.query(models.Location).filter(
        models.Location.is_active == True
    ).offset(skip).limit(limit).all()
    
    return locations

@router.get("/{location_id}", response_model=schemas.LocationResponse)
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
    
    return location