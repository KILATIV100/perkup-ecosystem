from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

from app.database import engine, get_db, Base
from app import models, schemas

# Створюємо таблиці
Base.metadata.create_all(bind=engine)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PerkUP API",
    description="Backend API для PerkUP Ecosystem",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Головна сторінка API"""
    return {
        "message": "🤖☕ PerkUP API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "locations": "/api/v1/locations",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Health check з перевіркою БД"""
    try:
        # Перевіряємо підключення до БД
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "perkup-backend",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return {
            "status": "unhealthy",
            "service": "perkup-backend",
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/api/v1/locations", response_model=list[schemas.Location])
def get_locations(db: Session = Depends(get_db)):
    """Отримати список локацій з БД"""
    logger.info("Getting locations from database")
    
    try:
        locations = db.query(models.Location).filter(
            models.Location.is_active == True
        ).all()
        
        logger.info(f"Found {len(locations)} locations")
        
        # Якщо локацій немає - повертаємо хардкод для тесту
        if not locations:
            logger.warning("No locations in database, returning hardcoded data")
            return [
                {
                    "id": 1,
                    "name": "Mark Mall",
                    "slug": "mark-mall",
                    "address": "Київська, 239, Бровари",
                    "city": "Бровари",
                    "latitude": 50.514794,
                    "longitude": 30.782308,
                    "radius_meters": 100,
                    "description": "Кав'ярня в ТРЦ Mark Mall",
                    "is_active": True,
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": None
                },
                {
                    "id": 2,
                    "name": "Парк Приозерний",
                    "slug": "park-priozerny",
                    "address": "вул. Фіалковського, 27а, Бровари",
                    "city": "Бровари",
                    "latitude": 50.501265,
                    "longitude": 30.754011,
                    "radius_meters": 100,
                    "description": "Кав'ярня біля парку",
                    "is_active": True,
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": None
                }
            ]
        
        return locations
        
    except Exception as e:
        logger.error(f"Error getting locations: {e}")
        # Fallback на хардкод якщо БД не працює
        return [
            {
                "id": 1,
                "name": "Mark Mall",
                "slug": "mark-mall",
                "address": "Київська, 239, Бровари",
                "city": "Бровари",
                "latitude": 50.514794,
                "longitude": 30.782308,
                "radius_meters": 100,
                "description": "Кав'ярня в ТРЦ Mark Mall",
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": None
            },
            {
                "id": 2,
                "name": "Парк Приозерний",
                "slug": "park-priozerny",
                "address": "вул. Фіалковського, 27а, Бровари",
                "city": "Бровари",
                "latitude": 50.501265,
                "longitude": 30.754011,
                "radius_meters": 100,
                "description": "Кав'ярня біля парку",
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": None
            }
        ]

@app.post("/api/v1/locations", response_model=schemas.Location)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    """Створити нову локацію"""
    db_location = models.Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_locationgit add backend/app/main.py