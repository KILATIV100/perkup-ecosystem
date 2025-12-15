"""Checkin endpoints"""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession, CurrentUser
from app.schemas.checkin import (
    CheckinCreate,
    CheckinResponse,
    CheckinSuccessResponse,
    CheckinHistoryResponse,
    CheckinError,
)
from app.services.checkin_service import CheckinService, CheckinError as ServiceError

router = APIRouter()


@router.post("", response_model=CheckinSuccessResponse)
async def create_checkin(
    checkin_data: CheckinCreate,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Perform a check-in at a location.

    Requires user to be within the location's check-in radius.
    Returns points and experience earned.
    """
    checkin_service = CheckinService(db)

    try:
        checkin, user_update = await checkin_service.create_checkin(
            current_user, checkin_data
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": e.code,
                "message": e.message,
                "details": e.details
            }
        )

    # Get location name for response
    location = await checkin_service.get_location_by_id(checkin.location_id)

    return CheckinSuccessResponse(
        success=True,
        checkin=CheckinResponse(
            id=checkin.id,
            location_id=checkin.location_id,
            location_name=location.name if location else "Unknown",
            user_latitude=float(checkin.user_latitude) if checkin.user_latitude else None,
            user_longitude=float(checkin.user_longitude) if checkin.user_longitude else None,
            distance_meters=checkin.distance_meters,
            points_earned=user_update["points_earned"],
            experience_earned=user_update["experience_earned"],
            checkin_date=checkin.checkin_date,
            created_at=checkin.created_at,
        ),
        user_updated=user_update
    )


@router.get("/history", response_model=CheckinHistoryResponse)
async def get_checkin_history(
    current_user: CurrentUser,
    db: DbSession,
    page: int = 1,
    per_page: int = 20
):
    """
    Get user's check-in history with pagination.
    """
    checkin_service = CheckinService(db)
    checkins, total = await checkin_service.get_user_checkins(
        current_user.id, page, per_page
    )

    # Get location names
    responses = []
    for checkin in checkins:
        location = await checkin_service.get_location_by_id(checkin.location_id)
        responses.append(CheckinResponse(
            id=checkin.id,
            location_id=checkin.location_id,
            location_name=location.name if location else "Unknown",
            user_latitude=float(checkin.user_latitude) if checkin.user_latitude else None,
            user_longitude=float(checkin.user_longitude) if checkin.user_longitude else None,
            distance_meters=checkin.distance_meters,
            points_earned=checkin.points_earned,
            experience_earned=checkin.experience_earned,
            checkin_date=checkin.checkin_date,
            created_at=checkin.created_at,
        ))

    return CheckinHistoryResponse(
        checkins=responses,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/can-checkin/{location_id}")
async def can_checkin(
    location_id: int,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Check if user can check in at a specific location.
    """
    checkin_service = CheckinService(db)
    can_checkin, reason = await checkin_service.can_checkin(
        current_user.id, location_id
    )

    return {
        "can_checkin": can_checkin,
        "reason": reason
    }
