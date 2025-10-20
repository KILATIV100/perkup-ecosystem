import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PerkUP API",
    version="1.0.0"
)

# CORS з environment variable
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "🤖☕ PerkUP API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/v1/locations")
def get_locations():
    return [
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