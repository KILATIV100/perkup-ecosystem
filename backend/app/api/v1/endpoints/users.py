"""User endpoints"""

from fastapi import APIRouter

from app.api.deps import DbSession, CurrentUser
from app.schemas.user import UserResponse, UserProfileResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: CurrentUser
):
    """
    Get current user's profile with extended information.
    """
    return UserProfileResponse.from_user(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Update current user's settings.
    """
    user_service = UserService(db)
    updated_user = await user_service.update(current_user, update_data)
    return UserResponse.model_validate(updated_user)


@router.get("/me/stats")
async def get_current_user_stats(
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get current user's statistics.
    """
    from app.services.leaderboard_service import LeaderboardService

    leaderboard_service = LeaderboardService(db)
    leaderboard_stats = await leaderboard_service.get_user_stats(current_user.id)

    return {
        "points": current_user.points,
        "experience": current_user.experience,
        "level": current_user.level,
        "total_checkins": current_user.total_checkins,
        "total_games_played": current_user.total_games_played,
        "best_game_score": current_user.best_game_score,
        "leaderboard": leaderboard_stats
    }
