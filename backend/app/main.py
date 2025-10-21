from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

from app.database import engine, get_db, Base
from app import models, schemas

# ТИМЧАСОВО: Створюємо таблиці при старті
try:
    Base.metadata.create_all(bind=engine)
    logging.info("✅ Database tables created successfully")
except Exception as e:
    logging.error(f"❌ Failed to create tables: {e}")

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
def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "perkup-backend"
    }

@app.get("/api/v1/locations")
def get_locations(db: Session = Depends(get_db)):
    """Отримати список локацій з БД"""
    logger.info("Getting locations from database")
    
    try:
        locations = db.query(models.Location).filter(
            models.Location.is_active == True
        ).all()
        
        logger.info(f"Found {len(locations)} locations")
        
        # Якщо локацій немає - повертаємо хардкод
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
                    "is_active": True
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
                    "is_active": True
                }
            ]
        
        return locations
        
    except Exception as e:
        logger.error(f"Error getting locations: {e}")
        # Fallback на хардкод
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
                "is_active": True
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
                "is_active": True
            }
        ]