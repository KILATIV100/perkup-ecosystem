"""API v1 package"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, locations, checkins, games, events, leaderboard

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(checkins.router, prefix="/checkins", tags=["checkins"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
