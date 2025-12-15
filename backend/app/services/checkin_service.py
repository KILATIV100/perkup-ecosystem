"""Checkin service - business logic for check-in operations"""

from datetime import datetime, date, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkin import Checkin
from app.models.location import Location
from app.models.user import User
from app.schemas.checkin import CheckinCreate, CheckinResponse
from app.utils.geo import is_within_radius
from app.core.config import settings


class CheckinError(Exception):
    """Custom exception for checkin errors"""

    def __init__(self, code: str, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class CheckinService:
    """Service for check-in operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_location_by_id(self, location_id: int) -> Location | None:
        """Get location by ID"""
        result = await self.db.execute(
            select(Location).where(Location.id == location_id)
        )
        return result.scalar_one_or_none()

    async def get_last_checkin(self, user_id: int, location_id: int) -> Checkin | None:
        """Get user's last checkin at a location"""
        result = await self.db.execute(
            select(Checkin)
            .where(
                Checkin.user_id == user_id,
                Checkin.location_id == location_id
            )
            .order_by(Checkin.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def can_checkin(self, user_id: int, location_id: int) -> tuple[bool, str | None]:
        """
        Check if user can check in at location.

        Returns:
            Tuple of (can_checkin, error_reason)
        """
        # Check if already checked in today at this location
        today = date.today()
        result = await self.db.execute(
            select(Checkin)
            .where(
                Checkin.user_id == user_id,
                Checkin.location_id == location_id,
                Checkin.checkin_date == today
            )
        )
        if result.scalar_one_or_none():
            return False, "cooldown_active"

        return True, None

    async def create_checkin(
        self,
        user: User,
        checkin_data: CheckinCreate
    ) -> tuple[Checkin, dict]:
        """
        Create a new check-in.

        Returns:
            Tuple of (checkin, user_update_info)

        Raises:
            CheckinError: If check-in is not possible
        """
        # Get location
        location = await self.get_location_by_id(checkin_data.location_id)
        if not location:
            raise CheckinError("location_not_found", "Location not found")

        if not location.is_active:
            raise CheckinError("location_inactive", "Location is not active")

        # Check distance
        is_within, distance = is_within_radius(
            checkin_data.latitude,
            checkin_data.longitude,
            float(location.latitude),
            float(location.longitude),
            location.checkin_radius_meters
        )

        if not is_within:
            raise CheckinError(
                "too_far",
                f"You are {distance}m away from the location. Maximum allowed: {location.checkin_radius_meters}m",
                {"distance": distance, "max_distance": location.checkin_radius_meters}
            )

        # Check cooldown
        can_checkin, error_reason = await self.can_checkin(user.id, location.id)
        if not can_checkin:
            raise CheckinError(
                "cooldown_active",
                "You have already checked in at this location today"
            )

        # Calculate rewards
        points_earned = 1  # Base points
        experience_earned = 10  # Base XP

        # Create checkin
        checkin = Checkin(
            user_id=user.id,
            location_id=location.id,
            user_latitude=checkin_data.latitude,
            user_longitude=checkin_data.longitude,
            distance_meters=distance,
            points_earned=points_earned,
            experience_earned=experience_earned,
            checkin_date=date.today(),
        )
        self.db.add(checkin)

        # Update location stats
        location.total_checkins += 1

        # Update user stats
        user.total_checkins += 1
        bonus = user.get_level_bonus()
        actual_points = int(points_earned * (1 + bonus))
        user.points += actual_points
        user.experience += experience_earned

        # Check level up
        new_level = user.calculate_level()
        if new_level > user.level:
            user.level = new_level

        await self.db.flush()
        await self.db.refresh(checkin)

        user_update = {
            "points": user.points,
            "experience": user.experience,
            "level": user.level,
            "total_checkins": user.total_checkins,
            "points_earned": actual_points,
            "experience_earned": experience_earned,
        }

        return checkin, user_update

    async def get_user_checkins(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[list[Checkin], int]:
        """Get user's checkin history with pagination"""
        # Count total
        count_result = await self.db.execute(
            select(func.count(Checkin.id)).where(Checkin.user_id == user_id)
        )
        total = count_result.scalar()

        # Get paginated results
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Checkin)
            .where(Checkin.user_id == user_id)
            .order_by(Checkin.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        checkins = result.scalars().all()

        return checkins, total
