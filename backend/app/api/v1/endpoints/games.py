"""Game endpoints"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession, CurrentUser
from app.schemas.game import (
    GameResponse,
    GameListResponse,
    GameSessionCreate,
    GameSessionEnd,
    GameSessionResponse,
    GameSessionStartResponse,
    GameSessionEndResponse,
)
from app.services.game_service import GameService, GameError

router = APIRouter()


@router.get("", response_model=GameListResponse)
async def get_games(db: DbSession):
    """
    Get all available games.
    """
    game_service = GameService(db)
    games = await game_service.get_all_games()

    return GameListResponse(
        games=[GameResponse.model_validate(g) for g in games]
    )


@router.get("/{slug}", response_model=GameResponse)
async def get_game(slug: str, db: DbSession):
    """
    Get game details by slug.
    """
    game_service = GameService(db)
    game = await game_service.get_game_by_slug(slug)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    return GameResponse.model_validate(game)


@router.post("/{slug}/sessions", response_model=GameSessionStartResponse)
async def start_game_session(
    slug: str,
    session_data: GameSessionCreate,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Start a new game session.
    """
    game_service = GameService(db)
    game = await game_service.get_game_by_slug(slug)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    if not game.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not active"
        )

    session = await game_service.start_session(
        current_user, game, session_data.platform
    )

    return GameSessionStartResponse(
        session_id=session.id,
        game=GameResponse.model_validate(game)
    )


@router.post("/sessions/{session_id}/end", response_model=GameSessionEndResponse)
async def end_game_session(
    session_id: UUID,
    session_data: GameSessionEnd,
    current_user: CurrentUser,
    db: DbSession
):
    """
    End a game session and submit score.
    """
    game_service = GameService(db)
    session = await game_service.get_session_by_id(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your session"
        )

    if session.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already completed"
        )

    try:
        session, points_earned, positions = await game_service.end_session(
            session,
            current_user,
            session_data.score,
            session_data.duration_seconds
        )
    except GameError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": e.code, "message": e.message}
        )

    game = await game_service.get_game_by_id(session.game_id)

    return GameSessionEndResponse(
        session=GameSessionResponse(
            id=session.id,
            game_id=session.game_id,
            game_name=game.name if game else "Unknown",
            score=session.score,
            duration_seconds=session.duration_seconds,
            points_earned=session.points_earned,
            experience_earned=session.experience_earned,
            is_completed=session.is_completed,
            created_at=session.created_at,
            completed_at=session.completed_at,
        ),
        points_earned=points_earned,
        leaderboard_position=positions
    )
