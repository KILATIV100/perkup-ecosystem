from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

from app.database import engine, get_db
from app import models, schemas

# Створюємо таблиці
models.Base.metadata.create_all(bind=engine)

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
    return {"status": "healthy", "service": "perkup-backend"}

@app.get("/api/v1/locations", response_model=list[schemas.Location])
def get_locations(db: Session = Depends(get_db)):
    """Отримати список локацій з БД"""
    logger.info("Getting locations from database")
    locations = db.query(models.Location).filter(models.Location.is_active == True).all()
    logger.info(f"Found {len(locations)} locations")
    return locations

@app.post("/api/v1/locations", response_model=schemas.Location)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    """Створити нову локацію"""
    db_location = models.Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location