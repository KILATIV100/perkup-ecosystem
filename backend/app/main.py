from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.database import engine, Base
from app.config import settings

# Імпортуємо models ПЕРЕД створенням таблиць
from app.models import User, Location, Checkin  # ВАЖЛИВО!

# Import routers
from app.api import auth, locations, checkins, users

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Створюємо таблиці
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created")
except Exception as e:
    logger.error(f"❌ Failed to create tables: {e}")

app = FastAPI(
    title="PerkUP API",
    description="Backend API для PerkUP Ecosystem",
    version="1.0.0"
)

# CORS
origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(locations.router, prefix="/api/v1")
app.include_router(checkins.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "🤖☕ PerkUP API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "auth": "/api/v1/auth/telegram",
            "locations": "/api/v1/locations",
            "checkins": "/api/v1/checkins",
            "users": "/api/v1/users/me",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "perkup-backend",
        "database": "connected"
    }