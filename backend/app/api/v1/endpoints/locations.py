"""Location endpoints"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import DbSession
from app.models.location import Location
from app.schemas.location import LocationResponse, LocationListResponse

router = APIRouter()


@router.get("", response_model=LocationListResponse)
async def get_locations(db: DbSession):
    """
    Get all active locations.
    """
    result = await db.execute(
        select(Location)
        .where(Location.is_active == True)
        .order_by(Location.id)
    )
    locations = result.scalars().all()

    return LocationListResponse(
        locations=[LocationResponse.model_validate(loc) for loc in locations],
        total=len(locations)
    )


@router.get("/{slug}", response_model=LocationResponse)
async def get_location(slug: str, db: DbSession):
    """
    Get location details by slug.
    """
    result = await db.execute(
        select(Location).where(Location.slug == slug)
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    return LocationResponse.model_validate(location)
