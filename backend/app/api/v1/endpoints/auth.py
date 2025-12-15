"""Authentication endpoints"""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession
from app.core.security import validate_telegram_init_data, create_access_token
from app.schemas.auth import TelegramAuthRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post("/telegram", response_model=dict)
async def authenticate_telegram(
    request: TelegramAuthRequest,
    db: DbSession
):
    """
    Authenticate user via Telegram Mini App initData.

    This endpoint validates the initData from Telegram WebApp
    and returns a JWT token for subsequent requests.
    """
    try:
        telegram_data = validate_telegram_init_data(request.init_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

    # Get or create user
    user_service = UserService(db)
    user, is_new = await user_service.get_or_create(telegram_data)

    # Generate JWT token
    access_token = create_access_token(user.id, user.telegram_id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
        "is_new_user": is_new
    }
