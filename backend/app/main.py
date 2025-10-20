from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PerkUP API",
    description="Backend API для PerkUP Ecosystem",
    version="1.0.0"
)

# CORS - ДОЗВОЛЯЄМО ВСІМ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Дозволяємо всім доменам
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Головна сторінка API"""
    logger.info("Root endpoint called")
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
    logger.info("Health check called")
    return {"status": "healthy", "service": "perkup-backend"}

@app.get("/api/v1/locations")
def get_locations():
    """Отримати список локацій"""
    logger.info("Get locations called")
    
    locations = [
        {
            "id": 1,
            "name": "Mark Mall",
            "address": "Київська, 239, Бровари",
            "latitude": 50.514794,
            "longitude": 30.782308,
            "radius_meters": 100,
            "is_active": True
        },
        {
            "id": 2,
            "name": "Парк Приозерний",
            "address": "вул. Фіалковського, 27а, Бровари",
            "latitude": 50.501265,
            "longitude": 30.754011,
            "radius_meters": 100,
            "is_active": True
        }
    ]
    
    logger.info(f"Returning {len(locations)} locations")
    return locations

# Додатковий endpoint для CORS preflight
@app.options("/api/v1/locations")
def options_locations():
    """CORS preflight"""
    return {"message": "OK"}