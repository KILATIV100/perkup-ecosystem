"""Event endpoints"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Literal

from app.api.deps import DbSession, CurrentUser, OptionalUser
from app.schemas.event import (
    EventResponse,
    EventListResponse,
    EventParticipantResponse,
    JoinEventResponse,
    EventProgressResponse,
)
from app.services.event_service import EventService, EventError

router = APIRouter()


@router.get("", response_model=EventListResponse)
async def get_events(
    db: DbSession,
    status: Literal["active", "upcoming", "past"] | None = None,
    event_type: Literal["promo", "tournament", "offline", "challenge"] | None = None,
    featured: bool = False
):
    """
    Get events with optional filters.
    """
    event_service = EventService(db)
    events = await event_service.get_events(
        status=status,
        event_type=event_type,
        featured_only=featured
    )

    return EventListResponse(
        events=[EventResponse.model_validate(e) for e in events],
        total=len(events)
    )


@router.get("/{slug}", response_model=EventResponse)
async def get_event(slug: str, db: DbSession):
    """
    Get event details by slug.
    """
    event_service = EventService(db)
    event = await event_service.get_event_by_slug(slug)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return EventResponse.model_validate(event)


@router.post("/{slug}/join", response_model=JoinEventResponse)
async def join_event(
    slug: str,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Join an event.
    """
    event_service = EventService(db)
    event = await event_service.get_event_by_slug(slug)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    try:
        participation = await event_service.join_event(event, current_user)
    except EventError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": e.code, "message": e.message}
        )

    return JoinEventResponse(
        success=True,
        participation=EventParticipantResponse.model_validate(participation)
    )


@router.get("/{slug}/my-progress", response_model=EventProgressResponse)
async def get_event_progress(
    slug: str,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get user's progress in an event.
    """
    event_service = EventService(db)
    event = await event_service.get_event_by_slug(slug)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    participation = await event_service.get_participation(event.id, current_user.id)

    if not participation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not participating in this event"
        )

    return EventProgressResponse(
        participation=EventParticipantResponse.model_validate(participation),
        event=EventResponse.model_validate(event)
    )


@router.post("/{slug}/claim-rewards")
async def claim_event_rewards(
    slug: str,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Claim rewards for a completed event.
    """
    event_service = EventService(db)
    event = await event_service.get_event_by_slug(slug)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    participation = await event_service.get_participation(event.id, current_user.id)

    if not participation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not participating in this event"
        )

    try:
        rewards = await event_service.claim_rewards(participation)
    except EventError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": e.code, "message": e.message}
        )

    return {
        "success": True,
        "rewards": rewards
    }
